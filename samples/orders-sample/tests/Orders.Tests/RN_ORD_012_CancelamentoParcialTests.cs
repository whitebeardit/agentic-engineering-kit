using Orders.Domain;
using Orders.Domain.Specifications;
using Xunit;

namespace Orders.Tests;

/// <summary>
/// Prova executável de docs/regras/pedidos.md#RN-ORD-012 e de .specs/features/001-cancelamento-parcial/spec.md (CANC-01..07).
/// Um teste por cláusula EARS; o nome carrega o ID da regra e a cláusula.
/// </summary>
public class RN_ORD_012_CancelamentoParcialTests
{
    private static Order PedidoAbertoComDoisItens(out OrderItem a, out OrderItem b)
    {
        var order = new Order(Guid.NewGuid());
        a = order.AddItem("SKU-A", 2, Money.Brl(50));   // 100,00
        b = order.AddItem("SKU-B", 1, Money.Brl(30));   //  30,00
        return order;
    }

    // ----- CANC-06 · WHILE o pedido não está Aberto, não é elegível -----

    [Fact]
    public void RN_ORD_012_WHILE_pedido_Aberto_SHALL_ser_elegivel_para_cancelamento_de_item()
    {
        var order = PedidoAbertoComDoisItens(out _, out _);

        var elegivel = new PedidoElegivelParaCancelamento().IsSatisfiedBy(order);

        Assert.True(elegivel);
    }

    [Fact]
    public void RN_ORD_012_WHILE_pedido_Faturado_SHALL_nao_ser_elegivel_para_cancelamento_de_item()
    {
        var order = PedidoAbertoComDoisItens(out _, out _);
        order.Invoice();

        var elegivel = new PedidoElegivelParaCancelamento().IsSatisfiedBy(order);

        Assert.False(elegivel);
    }
}
