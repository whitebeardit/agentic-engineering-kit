namespace Erp.Legacy;

/// <summary>
/// Código herdado (2014). Ninguém explica os números. Antes de qualquer refactor, o characterization test
/// (tests/Legacy) congela o comportamento atual — o que faz hoje, não o que deveria.
/// </summary>
public static class CalculadoraFrete
{
    public static decimal Calcular(string uf, decimal pesoKg, decimal valorPedido, bool clienteVip)
    {
        decimal frete = uf switch
        {
            "SP" => 12m,
            "RJ" => 15m,
            "MG" => 17.5m,
            _ => 25m,
        };

        if (pesoKg > 10)
        {
            frete += (pesoKg - 10) * 1.8m;
        }

        if (valorPedido >= 300)
        {
            frete *= 0.5m;
        }

        if (clienteVip && valorPedido >= 150)
        {
            frete = 0;
        }

        if (uf is "AM" or "RR")
        {
            frete += 9.9m;
        }

        return Math.Round(frete, 2, MidpointRounding.AwayFromZero);
    }
}
