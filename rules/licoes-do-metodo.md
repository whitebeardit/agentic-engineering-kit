# Lições do método — valem em toda sessão

Seis regras que nasceram de defeitos que passaram por todos os gates. A versão longa, com o defeito de origem de cada
uma, está em `docs/licoes-do-metodo.md` do kit. Esta regra não tem `paths`: carrega em toda sessão.

1. **Nenhuma afirmação sobre o código sem `arquivo:linha`.** Mecanismo, gate ou teste que você diz existir tem o
   arquivo e a linha ao lado; sem referência, a frase sai ou vira pergunta.
2. **Falha de acesso não é evidência de ausência.** Fonte que não respondeu, PDF que não abriu ou API sem permissão não
   viram "não existe"; toda conclusão negativa declara como procurou.
3. **Confiança baixa não recebe aspas.** Citação literal só com ficha (URL, data de acesso, confiança); fonte de
   confiança média ou baixa entra parafraseada e não sustenta número.
4. **Contagem sobre si mesmo se reconta no artefato construído.** "Os N arquivos", "as três regras": reconte na ref
   versionada antes da revisão, com o comando que conta.
5. **Chave de sanitização precisa de fronteira de palavra.** Teste com o termo proibido dentro de palavras maiores e
   rode o verificador de nomes sobre a saída do sanitizador.
6. **Um limiar de forma mede o que é entregue, não o que é escrito.** Pelo menos um gate abre o artefato construído
   (bundle, página, resposta) em vez de ler só a fonte.
