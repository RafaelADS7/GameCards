from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.db.models import Avg
from .models import Jogo, Avaliacao
from .forms import JogoForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required


# VIEWS PUBLICAS

# Listar todos os jogos
class JogoListView(ListView):
    model = Jogo
    template_name = 'jogos/pages/home.html' 
    context_object_name = 'jogos' 

# View pública para mostrar os detalhes de um jogo específico com média de avaliação
class JogoDetailView(DetailView):
    model = Jogo
    template_name = 'jogos/pages/detalhes.html' 
    context_object_name = 'jogo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jogo = self.object
        media_estrelas = Avaliacao.objects.filter(jogo=jogo).aggregate(Avg("estrelas"))["estrelas__avg"] or 0
        context["media_estrelas"] = round(media_estrelas, 1)
        return context

# View para registrar avaliação (usuário logado obrigatório)
@login_required
def avaliar_jogo(request, jogo_id):
    jogo = get_object_or_404(Jogo, id=jogo_id)

    if request.method == "POST":
        estrelas = int(request.POST.get("estrelas", 0))
        Avaliacao.objects.update_or_create(usuario=request.user, jogo=jogo, defaults={"estrelas": estrelas})

        # Calcula a nova média de estrelas após a avaliação
        media_estrelas = Avaliacao.objects.filter(jogo=jogo).aggregate(Avg("estrelas"))["estrelas__avg"] or 0

        return JsonResponse({"success": True, "media_estrelas": round(media_estrelas, 1)})

    return JsonResponse({"success": False})

# VIEWS PRIVADAS

class JogoUnifiedView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'jogos/pages/jogos_crud.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, pk=None):
        if pk:
            jogo = get_object_or_404(Jogo, pk=pk)
            form = JogoForm(instance=jogo)
        else:
            form = JogoForm()
        jogos = Jogo.objects.all()
        return render(request, self.template_name, {'form': form, 'jogos': jogos, 'editando': pk})

    def post(self, request, pk=None):
        if pk:
            jogo = get_object_or_404(Jogo, pk=pk)
            form = JogoForm(request.POST, request.FILES, instance=jogo)
        else:
            form = JogoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('jogos_unificados')

        jogos = Jogo.objects.all()
        return render(request, self.template_name, {'form': form, 'jogos': jogos, 'editando': pk})

@method_decorator(require_POST, name='dispatch')
class JogoDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    def post(self, request, pk):
        jogo = get_object_or_404(Jogo, pk=pk)
        jogo.delete()
        return redirect('jogos_unificados')
