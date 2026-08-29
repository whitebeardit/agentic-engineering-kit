// Whitebeard · Agentic Engineering Kit — regra de arquitetura como teste (ArchUnitNET).
// Mensagem escrita para o agente: cita o ADR e o passo de correção.
// dotnet add package TngTech.ArchUnitNET.xUnit
using ArchUnitNET.Domain;
using ArchUnitNET.Loader;
using ArchUnitNET.xUnit;
using Xunit;
using static ArchUnitNET.Fluent.ArchRuleDefinition;

public class ArchitectureTests
{
    private static readonly Architecture Arch = new ArchLoader()
        .LoadAssemblies(typeof(Orders.Domain.Marker).Assembly,
                        typeof(Orders.Application.Marker).Assembly,
                        typeof(Orders.Infrastructure.Marker).Assembly,
                        typeof(Orders.Api.Marker).Assembly)
        .Build();

    private static readonly IObjectProvider<IType> Domain =
        Types().That().ResideInNamespace("Orders.Domain", true).As("Domain");
    private static readonly IObjectProvider<IType> Infrastructure =
        Types().That().ResideInNamespace("Orders.Infrastructure", true).As("Infrastructure");
    private static readonly IObjectProvider<IType> Api =
        Types().That().ResideInNamespace("Orders.Api", true).As("Api");

    [Fact]
    public void Domain_nao_depende_de_Infrastructure()
    {
        Types().That().Are(Domain).Should().NotDependOnAny(Infrastructure)
            .Because("viola ADR-0003 (Domain é puro). Correção: mova o acesso a dados para uma interface em Domain e implemente em Infrastructure.")
            .Check(Arch);
    }

    [Fact]
    public void Controllers_nao_acessam_DbContext()
    {
        Types().That().Are(Api).Should().NotDependOnAny(
                Types().That().HaveNameEndingWith("DbContext"))
            .Because("viola ADR-0004 (controller sem regra nem persistência). Correção: chame um handler/serviço de Application.")
            .Check(Arch);
    }
}
