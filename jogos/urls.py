from django.urls import path
from .views import JogoListView, JogoDetailView, JogoUnifiedView, JogoDeleteView, avaliar_jogo

urlpatterns = [
    path('', JogoListView.as_view(), name='home'),
    path('jogo/<int:pk>/', JogoDetailView.as_view(), name='jogo_detalhes'),
    path('crud/jogo', JogoUnifiedView.as_view(), name='jogos_unificados'),
    path('editar/<int:pk>/', JogoUnifiedView.as_view(), name='jogo_editar'),
    path('excluir/<int:pk>/', JogoDeleteView.as_view(), name='jogo_excluir'),
    path('avaliar/<int:jogo_id>/', avaliar_jogo, name='avaliar_jogo'),
    
]
