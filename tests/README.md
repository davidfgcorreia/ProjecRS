# Estrutura dos Testes

Os testes estão organizados por módulo para facilitar a manutenção e aumentar a cobertura:

- `tests/api/`: Testes dos endpoints da API (FastAPI)
- `tests/db/`: Testes dos modelos e operações diretas no banco de dados
- `tests/services/`: Testes dos serviços e lógica de negócio
- `tests/integration/`: Testes de integração e cobertura de fluxo completo
- `tests/utils/`: Testes de utilitários e funções auxiliares

## Como rodar todos os testes

```bash
pytest --cov=app
```

## Observações
- Os testes de integração podem limpar o banco de dados entre execuções.
- Para garantir isolamento, utilize SQLite em memória para testes unitários e um banco separado para testes de API/integrados.
- Adapte/adicione fixtures conforme necessário para novos módulos.
