# Proxy LOD Plugin (Experimental)

> A plugin to generate Proxy LOD systems.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ProxyLODMeshReduction` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-13 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ProxyLODPlugin) | |

## 用途

ProxyLODPlugin 是一个实验性的编辑器插件，其核心功能是**生成代理 LOD（Level of Detail）系统**。它通过集成微软的 DirectXMesh 和 UVAtlas 库，为复杂的静态网格体（Static Mesh）提供一套自动化的处理流程，以生成优化后的低面数代理网格（Proxy Mesh）并为其重新生成 UV 布局。

这个插件解决的主要问题是：在大型开放世界或包含大量静态网格体的场景中，为每个物体手动创建和管理多个 LOD 级别是一项繁琐且耗时的工作。ProxyLODPlugin 旨在自动化这一过程，通过算法简化网格几何体并重新映射纹理坐标，从而在保持视觉可接受度的同时，显著降低渲染负载和内存占用。

## 使用场景

- **开放世界游戏开发**：为场景中大量的树木、岩石、建筑等静态资产自动生成远处使用的低精度代理模型。
- **建筑可视化**：为复杂的建筑模型创建用于远景渲染的简化版本。
- **性能优化**：当需要为现有资产快速生成一套 LOD 链，但手动建模成本过高时。
- **原型开发**：在项目早期快速为占位模型生成不同细节级别的版本。

## 蓝图用法

根据提供的源码分析，此插件主要作为**编辑器工具**集成，其核心功能（网格简化、UV 重映射）通过 C++ 库实现，并未暴露为蓝图可调用的节点。其使用通常通过编辑器菜单、命令行工具或自动化脚本触发，而非在运行时蓝图中直接调用。

## C++ 用法

此插件主要封装了第三方库（DirectXMesh, UVAtlas）的功能，其 C++ 用法更侧重于作为底层工具被其他编辑器模块或工具调用。

### 头文件引入

由于插件本身不提供面向用户的公共头文件，使用者通常需要依赖其构建的模块。在 `Build.cs` 中添加依赖后，可以使用其包含的第三方库功能。

```cpp
// 通常，使用者不会直接包含此插件的头文件。
// 而是通过依赖模块来使用其提供的网格处理功能。
// 例如，如果另一个编辑器工具需要调用网格简化，它会依赖 `ProxyLODMeshReduction` 模块。
```

### 基本用法

此插件的功能通常被封装在编辑器工具或自动化流程中。一个典型的调用流程可能如下（概念性代码，非直接 API）：

```cpp
// 假设在一个编辑器工具类中
#include "ProxyLODMeshReductionModule.h" // 假设的模块头文件

void UMyEditorTool::GenerateProxyLODForMesh(UStaticMesh* SourceMesh)
{
    // 1. 获取源网格数据
    FStaticMeshSourceModel& SourceModel = SourceMesh->GetSourceModel(0);
    FMeshDescription* MeshDescription = SourceModel.GetMeshDescription();

    // 2. 调用 ProxyLOD 模块提供的功能进行网格简化
    // （具体函数名需查阅插件源码，此处为示意）
    FMeshDescription SimplifiedMesh;
    ProxyLODMeshReduction::SimplifyMesh(MeshDescription, SimplifiedMesh, TargetTriangleCount);

    // 3. 调用 UVAtlas 功能为简化后的网格重新生成 UV
    ProxyLODMeshReduction::GenerateUVAtlas(SimplifiedMesh, ...);

    // 4. 将结果应用回 StaticMesh 资产
    // ...
}
```

### 进阶用法

结合网格处理和 UV 生成，可以实现更复杂的资产优化管线。例如，先使用 DirectXMesh 的功能清理和优化网格拓扑，再进行简化和 UV 重映射。

## Demo 示例

由于此插件主要作为内部工具链的一部分，没有独立的运行时 Demo。一个最小的使用示例是创建一个依赖此插件的编辑器模块。

**MyEditorTool.Build.cs**
```csharp
using UnrealBuildTool;

public class MyEditorTool : ModuleRules
{
    public MyEditorTool(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "UnrealEd",
            "ProxyLODMeshReduction" // 依赖 ProxyLOD 插件模块
        });

        PrivateDependencyModuleNames.AddRange(new string[] {
            "Slate",
            "SlateCore",
            "EditorStyle"
        });
    }
}
```

## 模块依赖

从 `ProxyLODMeshReduction.Build.cs` 分析，使用此插件需要以下依赖：

| 模块 | 用途 |
|---|---|
| `DirectXMesh` | 微软的 DirectX 网格处理库，用于网格清理、优化、法线计算等。 |
| `UVAtlas` | 微软的 UV 图集生成库，用于自动展开和打包 UV。 |

## 维护状态

### 近期更新

1.  **2916cb0bf8ea** (2024-05-15): `Add Windows Arm64 libs for ProxyLOD plugin.`
    *   **解读**：为插件添加了 Windows ARM64 架构的预编译库支持，表明插件仍在被维护以适应新的平台。
2.  **bc63a88d067f** (2024-04-18): `Redirect old cppcompilewarning properties to new *.CppCompileWarningSettings`
    *   **解读**：构建系统维护性更新，将旧的编译警告属性重定向到新的设置，无功能性变化。
3.  **761ea07fa23d** (2024-04-18): `UnrealBuildTool: Use warning level for undefined identifier property`
    *   **解读**：构建工具更新，调整了未定义标识符的警告级别，属于底层工具链改进。

### 维护评价

- **创建时间**：2017年12月，已有约7年历史。
- **最近更新**：最近的提交（2024年5月）是平台支持扩展，表明插件仍在维护中，但近期没有核心功能的更新或 bug 修复。
- **活跃度**：**维护不活跃**。虽然最近有提交，但主要是构建系统和平台适配的维护性工作，核心的网格简化与 UV 生成算法自创建以来似乎没有重大更新。
- **已知问题/限制**：
    1.  **实验性**：插件标记为 `IsBetaVersion=true`，且默认禁用，意味着其 API 和功能可能不稳定，不建议用于生产环境。
    2.  **平台限制**：仅支持 Win64 平台。
    3.  **依赖外部库**：核心功能依赖于微软的 DirectXMesh 和 UVAtlas，这些库本身可能不再活跃更新。
- **推荐使用**：**谨慎使用**。此插件适合用于**研究、原型开发或内部工具链**，了解代理 LOD 的生成原理。由于其实验性质、长期未更新的核心算法以及对外部库的依赖，**不推荐在正式的商业项目中作为核心功能依赖**。对于生产环境的 LOD 生成，建议评估 UE5 内置的自动 LOD 工具或更现代的第三方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ProxyLODPlugin)
- [官方文档]() （无）
- [测试用例]() （未在提供的信息中发现）