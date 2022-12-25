from django.urls import path

from . import views

urlpatterns = [
    path('', views.profile_upload, name="profile_upload"),
    path('show_data/<int:mac>', views.show_data, name="show_data"),
    path('analysis/<int:no>', views.analysis, name="analysis"),
    # path('sheet', views.create_sheet, name='create_sheet'),
    path('create_machine', views.machine_details, name='create_machine'),
    path('machines', views.machine_view, name='machine_view'),
    path('create_process/<int:machine>', views.process_details, name='process_details'),
    path('lead/<int:id>',views.lead_time,name='lead_time'),
    path('avg_lead_time',views.avg_lead_time),
    path('target/<int:id>', views.target, name='target'),
    path('operator/<slug:no>', views.operator_analysis, name='operator_analysis'),
    path('show_operators', views.show_operators, name='show_operators'),

    path('login/',views.loginPage,name="login"),
    path('register/',views.registerPage,name="register"),
    path('logout/',views.logoutUser,name="logout"),

    path('downtime/', views.downtime_calc, name='downtime'),
    path('show_order', views.show_order, name='show_order'),
]
