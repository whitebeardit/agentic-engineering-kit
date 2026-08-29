using Orders.Application.CancelOrderItem;
using Orders.Domain;
using Orders.Domain.Events;
using Orders.Infrastructure;

namespace Orders.Tests;

/// <summary>Prova executável de docs/regras/pedidos.md#RN-ORD-012. Um teste por cláusula EARS.</summary>
public class RN_ORD_012_CancelamentoParcialTests
{
    private static Order PedidoComDoisItens(out OrderItem a, out OrderItem b)
    {
        var order = new Order(Guid.NewGuid());
        a = order.AddItem("SKU-A", 2, Money.Brl(50));   // 100
        b = order.AddItem("SKU-B", 1, Money.Brl(30));   // 30
        return order;
    }

    [Fact]
    public void RN_ORD_012_WHEN_cliente_cancela_item_de_pedido_aberto_SHALL_recalcular_total()
    {
        var order = PedidoComDoisItens(out var a, out _);

        order.CancelItem(a.Id);

        Assert.Equal(Money.Brl(30), order.Total);
    }

    [Fact]
    public void RN_ORD_012_WHEN_cliente_cancela_item_SHALL_emitir_OrderItemCancelled_com_novo_total()
    {
        var order = PedidoComDoisItens(out var a, out _);

        order.CancelItem(a.Id);

        var evt = Assert.Single(order.Events.OfType<OrderItemCancelled>());
        Assert.Equal(order.Id, evt.OrderId);
        Assert.Equal(a.Id, evt.ItemId);
        Assert.Equal(Money.Brl(30), evt.NewTotal);
    }

    [Fact]
    public void RN_ORD_012_IF_pedido_faturado_THEN_SHALL_recusar_com_PedidoFaturado()
    {
        var order = PedidoComDoisItens(out var a, out _);
        order.Invoice();

        var ex = Assert.Throws<DomainRuleViolationException>(() => order.CancelItem(a.Id));

        Assert.Equal("RN-ORD-012", ex.RuleId);
        Assert.Equal(Money.Brl(130), order.Total);
        Assert.Empty(order.Events);
    }

    [Fact]
    public void RN_ORD_012_SHALL_CONTINUE_TO_ser_idempotente_ao_cancelar_o_mesmo_item_duas_vezes()
    {
        var order = PedidoComDoisItens(out var a, out _);

        order.CancelItem(a.Id);
        order.CancelItem(a.Id);

        Assert.Single(order.Events);
        Assert.Equal(Money.Brl(30), order.Total);
    }

    [Fact]
    public async Task RN_ORD_012_handler_orquestra_e_nao_decide()
    {
        var repo = new InMemoryOrderRepository();
        var order = PedidoComDoisItens(out var a, out _);
        await repo.SaveAsync(order, CancellationToken.None);
        var handler = new CancelOrderItemHandler(repo);

        var result = await handler.HandleAsync(new CancelOrderItemCommand(order.Id, a.Id), CancellationToken.None);

        Assert.Equal(Money.Brl(30), result.NewTotal);
        Assert.Single(result.Events);
    }
}
