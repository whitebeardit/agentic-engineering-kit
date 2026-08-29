using ArchUnitNET.Domain;
using ArchUnitNET.Loader;
using ArchUnitNET.xUnit;
using Orders.Application;
using Orders.Domain;
using Orders.Infrastructure;
using static ArchUnitNET.Fluent.ArchRuleDefinition;

namespace Orders.Tests;

/// <summary>ADR-0003 e ADR-0004 como testes. A mensagem é escrita para o agente: cita o ADR e o passo de correção.</summary>
public class ArchitectureTests
{
    private static readonly Architecture Arch = new ArchLoader()
        .LoadAssemblies(typeof(Order).Assembly, typeof(AssemblyMarker).Assembly, typeof(InMemoryOrderRepository).Assembly)
        .Build();

    private static readonly IObjectProvider<IType> Domain =
        Types().That().ResideInNamespaceMatching(@"^Orders\.Domain(\..*)?$").As("Domain");

    private static readonly IObjectProvider<IType> Application =
        Types().That().ResideInNamespaceMatching(@"^Orders\.Application(\..*)?$").As("Application");

    private static readonly IObjectProvider<IType> Infrastructure =
        Types().That().ResideInNamespaceMatching(@"^Orders\.Infrastructure(\..*)?$").As("Infrastructure");

    [Fact]
    public void Domain_nao_depende_de_Application_nem_de_Infrastructure()
    {
        Types().That().Are(Domain)
            .Should().NotDependOnAny(Application)
            .AndShould().NotDependOnAny(Infrastructure)
            .Because("viola ADR-0003 (Domain é puro). Correção: defina uma interface em Domain e implemente em Infrastructure.")
            .Check(Arch);
    }

    [Fact]
    public void Application_nao_depende_de_Infrastructure()
    {
        Types().That().Are(Application)
            .Should().NotDependOnAny(Infrastructure)
            .Because("viola ADR-0003 (Application fala com portas, não com adapters). Correção: receba IOrderRepository por injeção.")
            .Check(Arch);
    }

    [Fact]
    public void Application_nao_lanca_DomainRuleViolationException()
    {
        Types().That().Are(Application)
            .Should().NotDependOnAny(Types().That().Are(typeof(DomainRuleViolationException)))
            .Because("viola ADR-0004 (regra de negócio vive no domínio). Correção: mova a verificação para a entidade ou specification e chame-a do handler.")
            .Check(Arch);
    }
}
