# Lições do método — regras que nasceram de defeitos reais

Cada regra abaixo saiu de um defeito que passou por todos os gates existentes e foi pego depois: por um revisor
independente, por um leitor de teste ou pelo próprio autor lendo o artefato construído. Elas não são estilo — são
o conserto de um buraco que já custou retrabalho.

**Proveniência**: nasceram no repositório do livro *Cercando a IA*, o segundo repositório onde este kit foi aplicado.
As lições de lá que só valem para livro impresso (limiar de figura, quebra de página) ficaram lá. Estas seis
generalizam para qualquer repositório que trabalhe com agentes.

Como usar: leia na fase de especificação e na revisão. Cada regra traz **o defeito** que a originou e **como
verificar** que ela está sendo cumprida.

## 1. Nenhuma afirmação sobre o código sem `arquivo:linha`

Nunca afirme que um gate, um teste ou um mecanismo existe em um repositório sem apontar o arquivo e a linha.
Descreva apenas o que o artefato citado mostra. Inventar um mecanismo de enforcement é o mesmo defeito que inventar
um fato — e é mais perigoso, porque soa técnico.

- **Defeito de origem**: um capítulo afirmou que um repositório tinha um gate que ele não tinha. Passou pelos gates
  automáticos (nenhum lê prosa) e foi pego pelo revisor independente.
- **Como verificar**: toda afirmação de mecanismo, num documento ou numa descrição de PR, tem um `arquivo:linha` ao
  lado. Sem referência, a frase sai ou vira pergunta.

## 2. Falha de acesso não é evidência de ausência

Quando uma fonte não responde, isso não vira "não existe". Um formato que falhou não rebaixa a fonte: tente o
anúncio dos autores, a página alternativa, a cópia local (baixar e extrair o texto) antes de registrar "não
verificado na fonte primária". O mesmo vale para uma API que responde "sem permissão" — isso é falta de acesso, não
ausência de dado.

- **Defeito de origem**: uma referência foi registrada com confiança baixa porque um PDF não abriu por um caminho;
  a fonte primária estava disponível por outro. Em outra ocasião, uma auditoria concluiu "nenhum registro
  encontrado" a partir de uma resposta de permissão negada.
- **Como verificar**: toda conclusão negativa declara **como** procurou. "Não encontrei" sem método é opinião.

## 3. Confiança baixa não recebe aspas

Antes de citar uma ferramenta, norma ou estudo entre aspas, leia o nível de confiança da ficha e a coluna do que a
fonte **não** diz. Fonte de confiança média ou baixa entra apenas parafraseada, nunca como citação literal, e nunca
sustenta um número no corpo do texto.

- **Defeito de origem**: uma citação entre aspas foi montada a partir de fonte secundária; a redação exata não
  batia com o original.
- **Como verificar**: para cada par de aspas, existe uma ficha com URL, data de acesso e nível de confiança.

## 4. Contagem sobre si mesmo se reconta no artefato construído

Contagens que um artefato faz sobre si mesmo — "os N arquivos acima", "as três regras a seguir", "N testes" — não
têm fonte externa que o revisor possa conferir, e envelhecem em silêncio a cada edição. Reconte no artefato
**construído**, imediatamente antes da revisão, e prefira contar a partir da referência versionada, não da árvore
de trabalho.

- **Defeito de origem**: um título dizia um número e a caixa logo abaixo dizia outro; ninguém percebeu até a
  leitura do documento final.
- **Como verificar**: um comando que conta na ref pinada (por exemplo, listar a árvore da tag) e compara com o
  número escrito.

## 5. Chave de sanitização sem fronteira de palavra esconde vazamento

Substituição de texto para anonimizar precisa ancorar a chave em fronteira de palavra. Uma chave de uma palavra
sem âncora reescreve o interior de outras palavras: o termo proibido some da busca, o resultado fica com um híbrido
sem sentido, e o vazamento continua lá — agora invisível para o próprio gate que deveria pegá-lo.

- **Defeito de origem**: uma substituição sem fronteira produziu um domínio híbrido dentro de um trecho já
  "sanitizado"; o defeito foi encontrado por leitura humana, não pelo script.
- **Como verificar**: teste negativo com o termo proibido embutido dentro de palavras maiores; o resultado tem de
  ser o termo mapeado, não um híbrido. Rode o verificador de nomes sobre a **saída** do sanitizador.

## 6. Um limiar de forma mede o que é entregue, não o que é escrito

Esta é a mais cara das seis. Um gate que decide sobre a forma do resultado precisa medir o **artefato entregue**,
não o arquivo de origem. Contar linhas do fonte, caracteres do markdown ou tokens do template responde a uma
pergunta diferente da que importa — e o gate passa verde enquanto o defeito está no que o usuário recebe.

- **Defeito de origem**: o limiar que decidia se um painel podia ser quebrado contava linhas do arquivo. Um painel
  de 18 linhas de origem, com itens longos, renderizava cerca de 30 linhas na coluna final: passava no limiar,
  permanecia inquebrável e deixava meia página em branco. **Dois revisores encontraram o sintoma em documentos
  diferentes antes de alguém encontrar a causa.** O conserto foi estimar a altura impressa a partir da largura da
  coluna.
- **Generalização**: o mesmo vale para qualquer gate cujo objeto é o resultado — tamanho de bundle, latência
  percebida, contraste renderizado, tempo de resposta com a rede real. Se o gate lê a fonte, ele mede a intenção.
- **Como verificar**: existe pelo menos um gate que abre o artefato **construído** e o inspeciona. Se todos os
  gates leem apenas a fonte, esta regra não está sendo cumprida.

---

Uma lição só está fechada quando virou regra em algum lugar que alguém lê antes de errar de novo. Um comentário no
PR onde o defeito apareceu não conta: o próximo repositório não vai ler aquele PR.
