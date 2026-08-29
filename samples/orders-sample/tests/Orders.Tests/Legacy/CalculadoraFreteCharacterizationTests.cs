using Bogus;
using Erp.Legacy;

namespace Orders.Tests.Legacy;

/// <summary>
/// Characterization test: congela o comportamento ATUAL do legado com dados aleatórios de seed fixo.
/// O arquivo .verified.txt é o baseline aprovado por um humano. Mudou? É mudança de comportamento — explique no PR.
/// </summary>
public class CalculadoraFreteCharacterizationTests
{
    [Fact]
    public Task Congela_comportamento_atual_do_calculo_de_frete()
    {
        var faker = new Faker { Random = new Randomizer(20260827) };
        string[] ufs = ["SP", "RJ", "MG", "AM", "RR", "BA", "PR"];

        var casos = Enumerable.Range(1, 60).Select(i =>
        {
            var uf = faker.PickRandom(ufs);
            var peso = Math.Round(faker.Random.Decimal(0.1m, 40m), 2);
            var valor = Math.Round(faker.Random.Decimal(10m, 900m), 2);
            var vip = faker.Random.Bool();
            return new { Caso = i, Uf = uf, PesoKg = peso, ValorPedido = valor, Vip = vip, Frete = CalculadoraFrete.Calcular(uf, peso, valor, vip) };
        }).ToList();

        return Verifier.Verify(casos);
    }
}
