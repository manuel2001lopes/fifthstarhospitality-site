# Instagram da Fifth Star Hospitality: manual da publicação automática

Esta pasta é usada pela tarefa agendada que publica no Instagram (@fifthstarhospitality, conta Composio `fifthstarhospitality`, ig_user_id `29072812052374839`) à segunda, quarta e sexta.

## Calendário

| Dia | Tipo | O que é |
|---|---|---|
| Segunda | `dica` | Um erro comum de hotéis e alojamentos independentes e como se corrige. Prático, sem números inventados. |
| Quarta | `noticia` | Uma notícia ou dado do setor dos últimos 14 dias, com a nossa leitura para um hotel pequeno. Fonte sempre citada. |
| Sexta | `servico` | O que fazemos (diagnóstico, correções rápidas, acompanhamento) ou um caso real sem nomes. |

Em segunda e sexta publica-se também 1 story.

## Ordem de trabalho de cada execução

1. Ver `fila/`. Se houver um ficheiro com `publicar_em` igual à data de hoje (Lisboa), usar esse.
2. Se não houver, criar um post novo do tipo do dia. Ler `publicados/registo.md` para não repetir temas das últimas 6 semanas.
3. Atribuir `id` (`AAAA-MM-DD-tema`) e `numero` (`N.º XX`, o seguinte ao último do registo).
4. Gerar as imagens: `python3 fsh_ig.py post.json --out /tmp/out`. Ver cada imagem antes de publicar (texto cortado, gralhas, número errado).
5. Copiar os JPG para `social/posts/<id>/` neste ramo (`instagram-automatico`), mover o JSON da fila (ou o novo) para `publicados/`, acrescentar a linha ao registo, commit e push **para este ramo**. Nunca fazer merge para `main`: o site em produção não é tocado.
6. As imagens ficam públicas em `https://raw.githubusercontent.com/manuel2001lopes/fifthstarhospitality-site/instagram-automatico/social/posts/<id>/<id>-1.jpg` (confirmar com `curl -sI` que dá 200, pode demorar 1 a 2 minutos).
7. Publicar via Composio, conta `fifthstarhospitality`, ig_user_id `29072812052374839`: criar um contentor por imagem (`INSTAGRAM_POST_IG_USER_MEDIA` com `image_url` e `is_carousel_item: true`), depois `INSTAGRAM_CREATE_CAROUSEL_CONTAINER` com os ids e a legenda, depois `INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH`. Story: `INSTAGRAM_POST_IG_USER_MEDIA` com `media_type: STORIES` e depois publicar. Ver os nomes exatos dos campos com `COMPOSIO_GET_TOOL_SCHEMAS` antes.

## Regras de conteúdo (não negociáveis)

- Português de Portugal, tom direto e caloroso. Tratar o leitor por "você"/"o seu hotel".
- Sem travessões (—). Usar vírgula, ponto ou dois pontos.
- Nada de preços dos nossos serviços nos posts nem nas legendas.
- Só factos verificados numa fonte primária ou num órgão de comunicação credível: INE, Turismo de Portugal, Banco de Portugal, Eurostat, ALEP, AHP, AHRESP, Nova SBE, Público, Expresso, ECO, Jornal de Negócios, Publituris, Ambitur. Fonte no slide (campo `fonte`) e na legenda.
- Se um número não se confirma, não sai. Na quarta, se não houver notícia verificável, publica-se uma `dica`.
- Não copiar frases de artigos: resumir com palavras nossas. No máximo uma citação curta (menos de 15 palavras) e entre aspas.
- Exemplos inventados (conversas, pesquisas) levam o rótulo "Exemplo" ou o texto "Exemplo ilustrativo". Nunca nomes de hotéis reais como se fossem clientes.
- Sem resultados de clientes que não existam. Sem promessas de números.
- Sem logótipos de terceiros. Nomes de plataformas (Booking, Airbnb, Google) podem aparecer em texto.
- Fecho de cada carrossel: convite à análise de cortesia ou a mandar mensagem.
- Guia gratuito: quem envia a palavra GUIA por mensagem recebe automaticamente (ManyChat) o "teste dos 5 minutos" (https://fifthstarhospitality.com/teste-google.html). Em pelo menos um post em cada dois, a legenda inclui a linha: "Quer o nosso teste gratuito de 5 minutos? Envie GUIA por mensagem." Nos posts de dica e de serviço pode também ir no slide de fecho. Não pedir para comentar GUIA: só funciona por mensagem.
- Legenda: 80 a 180 palavras, primeira linha forte, frases curtas, fonte quando houver, CTA, 4 a 6 hashtags no fim (#hotelaria #alojamentolocal #reservasdiretas #turismoportugal e um ou dois do tema).

## Fotografias

Só fotos de `fotos/`, descritas em `fotos/fotos.json`. Nunca descarregar fotos da internet nem usar fotos de anúncios do Airbnb, Booking ou sites de hotéis (têm direitos de autor). Uma foto do banco nunca é apresentada como sendo de um cliente.

## Formato do JSON

```json
{
  "id": "2026-11-23-resposta-lenta",
  "numero": "N.º 05",
  "tipo_post": "dica",
  "publicar_em": "2026-11-23",
  "slides": [ { "tipo": "capa", "rotulo": "Erro comum", "titulo": "Primeira frase. Segunda frase em itálico tijolo." } ],
  "stories": [ ],
  "legenda": "texto da legenda"
}
```

Carrossel com 4 a 6 slides: o primeiro é `capa`, o último é `fecho`.

Tipos de slide (todos aceitam `rotulo`, `titulo`, `texto`):

| Tipo | Campos extra | Para quê |
|---|---|---|
| `capa`, `texto`, `fecho` | | Título e parágrafo |
| `numero` | `numero`, `fonte` | Um número grande (ex.: "45%") |
| `grafico` | `barras` [[rótulo, valor, "texto"]], `destaque` (índice), `fonte` | Comparar valores |
| `livro` | `linhas` [[a, b]], `total` [a, b], `fonte` | Tabela tipo livro de reservas |
| `passos` | `passos` [["01", "título", "texto"]] | Métodos |
| `lista`, `checklist` | `itens` | Listas numeradas ou com caixas |
| `pesquisa` | `consulta`, `resultados` [{etiqueta, url, nome, detalhe, destaque}] | Simular resultados do Google |
| `conversa` | `mensagens` [{de: "hospede"/"hotel", texto, hora, alerta}] | Simular pedidos de reserva |
| `citacao` | `citacao`, `autor` | Uma frase (nossa ou com autor real e fonte) |
| `foto` | `foto` (ficheiro em fotos/), `legenda` | Foto do banco |

O título divide-se no primeiro ". ": a segunda frase fica em itálico tijolo. O tamanho ajusta-se sozinho se o texto não couber, mas títulos com mais de 90 caracteres ficam pequenos: encurtar.
