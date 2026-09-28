# Ambiente de escrita científica no Oh My Pi

Configuração versada, revisores determinísticos e um *scientific gate* para a dissertação
IVF/SPEA2 (e os manuscritos associados), rodando dentro do [Oh My Pi (OMP)](https://github.com/can1357/oh-my-pi)
sem alterar o ambiente OMP global. Documentos:

- **`research.md`** — pesquisa externa: fontes, decisões (ADOPT/ADAPT/REJECT/EXPERIMENT), incertezas.
- **`decisoes.md`** — o que foi adotado/rejeitado com motivo.
- **`arquitetura.md`** — arquivos, papéis de modelo, fluxo `/gate`, onde cada decisão vive.
- **`usage.md`** — guia diário (iniciar, escrever, revisar, auditar, trocar modelos).
- **`evaluation.md`** — resultados das rodadas de teste (testes A–J e comparações de modelo).

Pastas na raiz do repo:

- `.omp/RULES.md`, `.omp/config.yml`, `.omp/agents/`, `.omp/skills/`, `.omp/commands/`
  (comandos: `/revise`, `/draft-section`, `/gate`, `/verify-evidence`, `/audit-numbers`,
  `/final-pass`)
- `.omp/science/overlay.yml`, `.omp/science/CONTEXT.md` e `.omp/science/models.yml`
  (carregados pelo launcher; o último empresta as credenciais do OMP normal)
- `scripts/omp-science` (launcher)
- `scripts/science/` (prose_audit, claims, latex_check, bib_check, omp_env_check)
- `tests/omp-science/` (fixtures e gabarito dos testes A–J)

## Início rápido

```bash
scripts/omp-science            # usa o login do OMP normal; avisa se faltar
scripts/omp-science --check    # diagnóstico determinístico
make thesis-lint               # prosa + LaTeX + bib (verificadores determinísticos)
```

## Princípios

1. **Nada é invenção**: invariantes no `.omp/RULES.md`; sem fonte verificável, marcador
   `[NÃO VERIFICADO]` e aviso ao autor.
2. **Nada é mudança silenciosa no manuscrito**: revisores produzem achados; o autor
   aceita; o editor altera apenas os achados aceitos; `claims.py diff` mostra exatamente
   o que mudou de número, citação, rótulo ou força.
3. **Revisores ≠ escritor**: revisores em família de modelo diferente, subagentes com
   contexto novo, sem fallback cruzando famílias.
4. **Custo por acionamento**: skills carregam corpo sob demanda (`skill://…`); revisores
   leem referências só quando a tarefa exige.
5. **Toda rodada deixa rastro**: `.omp/runs/` (gitignored) por rodada, `git diff` dos
   `.tex` e proposta de entrada em `AI_ASSISTANCE_LOG.md` quando houver participação
   material de IA (Portaria CNPq nº 2.664/2026).
