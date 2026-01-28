from django.urls import path

from .views import (ScoreListView, ScoreCreateView, ScoreUpdateView, ScoreDeleteView, ScoreDeleteMultipleView,
                    score_export, score_import, ScoreDetailView, MyScoreListView)

urlpatterns = [
    path('', ScoreListView.as_view(), name='score_list'),
    path('create/', ScoreCreateView.as_view(), name='score_create'),
    path('<int:pk>/update/', ScoreUpdateView.as_view(), name='score_update'),
    path('<int:pk>/delete/', ScoreDeleteView.as_view(), name='score_delete'),
    path('delete_multiple/', ScoreDeleteMultipleView.as_view(), name='score_delete_multiple'),
    path('<int:pk>/detail', ScoreDetailView.as_view(), name='score_detail'),
    path('export/', score_export, name='score_export'),
    path('import/', score_import, name='score_import'),
    path('my_score/', MyScoreListView.as_view(), name='my_score'),
 ]