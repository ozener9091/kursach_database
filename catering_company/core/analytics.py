
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncMonth
from core.models import (
    Dish, Product, Employee, Report, ReportDish, Delivery
)
from datetime import datetime, timedelta


def get_available_analytics_data(user):
    """Возвращает доступные данные для аналитики в зависимости от роли пользователя"""
    data = {
        'has_dish_data': user.has_perm('core.view_dish'),
        'has_product_data': user.has_perm('core.view_product'),
        'has_employee_data': user.has_perm('core.view_employee'),
        'has_report_data': user.has_perm('core.view_report'),
        'has_delivery_data': user.has_perm('core.view_delivery'),
        'has_request_data': user.has_perm('core.view_request'),
    }
    
    if data['has_dish_data']:
        data['dish_count'] = Dish.objects.count()
    if data['has_product_data']:
        data['product_count'] = Product.objects.count()
    if data['has_employee_data']:
        data['employee_count'] = Employee.objects.count()
    if data['has_report_data']:
        data['report_count'] = Report.objects.count()
    
    return data


def generate_charts_data(user, start_date=None, end_date=None):
    """Генерирует данные для графиков с возможностью фильтрации по дате"""
    charts_data = []
    
    date_filter = {}
    if start_date:
        date_filter['date__gte'] = start_date
    if end_date:
        date_filter['date__lte'] = end_date
    
    if user.has_perm('core.view_dish') and user.has_perm('core.view_reportdish'):
        try:
            top_dishes_query = ReportDish.objects.select_related('report').values('dish__name')
            
            if start_date or end_date:
                top_dishes_query = top_dishes_query.filter(report__date__range=[start_date, end_date])
            
            top_dishes = top_dishes_query.annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')[:5]
            
            if top_dishes:
                dish_names = [item['dish__name'] for item in top_dishes if item['dish__name']]
                quantities = [float(item['total_quantity'] or 0) for item in top_dishes]
                
                charts_data.append({
                    'title': 'Топ-5 блюд по количеству продаж',
                    'chart_id': 'top_dishes_chart',
                    'chart_type': 'bar',
                    'x_data': dish_names,
                    'y_data': quantities,
                    'x_label': 'Блюда',
                    'y_label': 'Количество',
                    'color': 'skyblue'
                })
        except Exception as e:
            print(f"Error generating top dishes chart: {e}")
    
    if user.has_perm('core.view_dish') and user.has_perm('core.view_reportdish'):
        try:
            sales_by_group_query = ReportDish.objects.select_related('dish', 'dish__assortment_group', 'report').values(
                'dish__assortment_group__name'
            )
            
            if start_date or end_date:
                sales_by_group_query = sales_by_group_query.filter(report__date__range=[start_date, end_date])
            
            sales_by_group = sales_by_group_query.annotate(
                total_revenue=Sum(F('quantity') * F('dish__price'))
            ).order_by('-total_revenue')
            
            if sales_by_group:
                group_names = [item['dish__assortment_group__name'] for item in sales_by_group if item['dish__assortment_group__name']]
                revenues = [float(item['total_revenue'] or 0) for item in sales_by_group]
                
                charts_data.append({
                    'title': 'Выручка по группам ассортимента',
                    'chart_id': 'revenue_by_group_chart',
                    'chart_type': 'bar',
                    'x_data': group_names,
                    'y_data': revenues,
                    'x_label': 'Группы ассортимента',
                    'y_label': 'Выручка (₽)',
                    'color': 'lightgreen'
                })
        except Exception as e:
            print(f"Error generating revenue by group chart: {e}")
    
    if user.has_perm('core.view_product'):
        try:
            low_stock_products = Product.objects.filter(
                remaining_stock__lt=20
            ).order_by('remaining_stock')[:10]
            
            if low_stock_products:
                product_names = [p.name for p in low_stock_products]
                stock_levels = [float(p.remaining_stock) for p in low_stock_products]
                
                charts_data.append({
                    'title': 'Продукты с низким остатком',
                    'chart_id': 'low_stock_chart',
                    'chart_type': 'bar',
                    'x_data': product_names,
                    'y_data': stock_levels,
                    'x_label': 'Продукты',
                    'y_label': 'Остаток',
                    'color': 'orange'
                })
        except Exception as e:
            print(f"Error generating low stock chart: {e}")
    
    if user.has_perm('core.view_delivery'):
        try:
            
            deliveries_query = Delivery.objects.all()
            
            if start_date:
                deliveries_query = deliveries_query.filter(date__gte=start_date)
            if end_date:
                deliveries_query = deliveries_query.filter(date__lte=end_date)
        
            if not start_date and not end_date:
                start_date_calc = datetime.now() - timedelta(days=365)
                deliveries_query = deliveries_query.filter(date__gte=start_date_calc)
            
            monthly_deliveries = deliveries_query.annotate(
                month=TruncMonth('date')
            ).values('month').annotate(
                delivery_count=Count('id')
            ).order_by('month')
            
            if monthly_deliveries:
                months = [item['month'].strftime('%Y-%m') for item in monthly_deliveries]
                counts = [item['delivery_count'] for item in monthly_deliveries]
                
                charts_data.append({
                    'title': 'Количество поставок по месяцам',
                    'chart_id': 'monthly_deliveries_chart',
                    'chart_type': 'line',
                    'x_data': months,
                    'y_data': counts,
                    'x_label': 'Месяц',
                    'y_label': 'Количество поставок',
                    'color': 'purple'
                })
        except Exception as e:
            print(f"Error generating deliveries chart: {e}")
    
    if user.has_perm('core.view_dish'):
        try:
            avg_price_by_group = Dish.objects.values(
                'assortment_group__name'
            ).annotate(
                avg_price=Avg('price')
            ).order_by('-avg_price')
            
            if avg_price_by_group:
                group_names = [item['assortment_group__name'] for item in avg_price_by_group if item['assortment_group__name']]
                avg_prices = [float(item['avg_price'] or 0) for item in avg_price_by_group]
                
                charts_data.append({
                    'title': 'Средняя цена блюд по группам',
                    'chart_id': 'avg_price_chart',
                    'chart_type': 'bar',
                    'x_data': group_names,
                    'y_data': avg_prices,
                    'x_label': 'Группы ассортимента',
                    'y_label': 'Средняя цена (₽)',
                    'color': 'coral'
                })
        except Exception as e:
            print(f"Error generating avg price chart: {e}")
    
    return charts_data
