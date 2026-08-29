using Orders.Domain;
using Orders.Domain.Events;
using Orders.Domain.Specifications;

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

    // ----- CANC-01 · WHEN cancela item de pedido Aberto, SHALL marcar cancelado e recalcular o total -----

    [Fact]
    public void RN_ORD_012_WHEN_cliente_cancela_item_de_pedido_Aberto_SHALL_marcar_cancelado_e_recalcular_total()
    {
        var order = PedidoAbertoComDoisItens(out var a, out _);

        order.CancelItem(a.Id);

        Assert.True(a.Cancelled);
        Assert.Equal(Money.Brl(30), order.Total);
    }

    // ----- CANC-02 · WHEN cancela item, SHALL emitir exatamente um OrderItemCancelled com OrderId, ItemId e NewTotal -----

    [Fact]
    public void RN_ORD_012_WHEN_cliente_cancela_item_SHALL_emitir_um_OrderItemCancelled_com_OrderId_ItemId_e_NewTotal()
    {
        var order = PedidoAbertoComDoisItens(out var a, out _);

        order.CancelItem(a.Id);

        var evt = Assert.Single(order.Events.OfType<OrderItemCancelled>());
        Assert.Equal(order.Id, evt.OrderId);
        Assert.Equal(a.Id, evt.ItemId);
        Assert.Equal(Money.Brl(30), evt.NewTotal);
    }

    // ----- CANC-03 · IF pedido faturado THEN SHALL recusar com RuleId RN-ORD-012 sem alterar total, itens ou eventos -----

    [Fact]
    public void RN_ORD_012_IF_pedido_faturado_THEN_SHALL_recusar_com_RuleId_RN_ORD_012_sem_alterar_o_pedido()
    {
        var order = PedidoAbertoComDoisItens(out var a, out _);
        order.Invoice();

        var ex = Assert.Throws<DomainRuleViolationException>(() => order.CancelItem(a.Id));

        Assert.Equal("RN-ORD-012", ex.RuleId);
        Assert.False(a.Cancelled);
        Assert.Equal(Money.Brl(130), order.Total);
        Assert.Empty(order.Events);
    }

    // ----- CANC-04 · SHALL ser idempotente: duas vezes → um único evento e o mesmo total -----

    [Fact]
    public void RN_ORD_012_SHALL_ser_idempotente_ao_cancelar_o_mesmo_item_duas_vezes()
    {
        var order = PedidoAbertoComDoisItens(out var a, out _);

        order.CancelItem(a.Id);
        order.CancelItem(a.Id);

        Assert.Single(order.Events.OfType<OrderItemCancelled>());
        Assert.Equal(Money.Brl(30), order.Total);
    }

    // ----- CANC-05 · IF item não pertence ao pedido THEN SHALL recusar sem alterar o pedido -----

    [Fact]
    public void RN_ORD_012_IF_item_nao_pertence_ao_pedido_THEN_SHALL_recusar_sem_alterar_o_pedido()
    {
        var order = PedidoAbertoComDoisItens(out _, out _);

        var ex = Assert.Throws<DomainRuleViolationException>(() => order.CancelItem(Guid.NewGuid()));

        Assert.Equal("RN-ORD-012", ex.RuleId);
        Assert.Equal(Money.Brl(130), order.Total);
        Assert.Empty(order.Events);
    }

    // ----- Edge (CANC-01) · WHEN o último item é cancelado, SHALL recalcular o total para 0,00 BRL -----

    [Fact]
    public void RN_ORD_012_WHEN_ultimo_item_e_cancelado_SHALL_recalcular_total_para_zero()
    {
        var order = PedidoAbertoComDoisItens(out var a, out var b);

        order.CancelItem(a.Id);
        order.CancelItem(b.Id);

        Assert.Equal(Money.Brl(0), order.Total);
        Assert.Equal(2, order.Events.OfType<OrderItemCancelled>().Count());
    }
}
