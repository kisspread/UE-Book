# Shader Toolkit

> A suite of tools to analyze your projects build and shaders to help reduce shader and material permutations.

| 属性 | 值 |
|---|---|
| 中文名 | 着色器工具包 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ShaderAuditCore` (EditorAndProgram), `ShaderAudit` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ShaderToolkit) | |

## 用途

Shader Toolkit 是一套用于分析项目构建产物中着色器（Shader）和材质（Material）复杂性的编辑器工具套件。它旨在帮助开发者识别并优化可能导致构建时间过长、包体过大或运行时性能问题的着色器变体（Permutations）和材质排列（Permutations）。

该插件的核心功能包括：
1.  **SHK 文件扫描与管理**：从本地缓存或远程 NAS 位置扫描并管理 Stable Shader Key (`.shk`) 文件，这些文件记录了着色器的唯一标识和依赖关系。
2.  **着色器审计会话**：加载、解析并构建一个包含所有着色器条目的“审计会话”，为分析提供统一的数据源。
3.  **可视化分析**：提供多种视图来分析着色器成本，包括：
    *   **成本树状图 (Cost Treemap)**：按文件夹或材质继承层次展示每个资产/材质消耗的着色器数量或大小。
    *   **统计电子表格 (Stat Spreadsheet)**：以表格形式展示按材质域、着色器频率、顶点工厂类型等维度聚合的着色器计数和大小。
    *   **原始 SHK 条目列表**：查看所有着色器条目的详细字段，并支持高级过滤。
    *   **材料差异比较 (Material Diff)**：对比两个审计会话（例如不同 CL 或分支），精确识别新增、移除或更改的材质。
4.  **过滤与探索**：提供强大的过滤语法，允许用户按资产路径、着色器类型、哈希、大小、引用计数等条件筛选着色器，以便聚焦于问题根源。

**为什么存在？** 在大型游戏项目中，材质和着色器变体的数量会随着美术资产的增加而爆炸式增长，这不仅导致构建时间漫长，还会增加包体体积和运行时内存占用。Shader Toolkit 为开发者和 TA（技术美术）提供了深入的数据洞察，使他们能够做出明智的优化决策，例如合并材质、减少材质参数开关、或移除未使用的着色器功能。

## 使用场景

-   你的项目构建时间异常漫长，怀疑着色器编译是瓶颈之一。
-   你需要分析游戏包体中着色器资产所占的空间，并找出占用最大的材质。
-   你希望理解项目材质的继承结构，避免过深或过复杂的材质实例链。
-   你需要对比两个不同版本（如 changelist 或分支）之间的材质变化，以评估性能影响。
-   作为技术美术或图形程序员，你需要一个可视化工具来探索和优化项目的着色器排列。

## 蓝图用法

此插件主要为编辑器扩展和编程接口，其核心功能通过 C++ 和 Slate UI 提供。它本身不暴露设计时蓝图节点，但提供了扩展点，允许其他模块通过“模块化特性”（Modular Features）向其界面注入自定义视图和功能。

### 核心扩展点

要扩展 Shader Audit 的视图界面，你可以实现 `IShaderAuditExtension` 接口。

| 接口/类 | 说明 |
|---|---|
| `IShaderAuditExtension` | 核心扩展接口。实现此接口并注册到 `IModularFeatures`，即可向 Shader Audit 会话视图添加自定义工具栏按钮和标签页。 |
| `FShaderAuditExtensionContribution` | 描述一个扩展对会话视图的具体贡献，如一个视图标签页及其工厂函数，或一个工具栏部件。 |

### 注册扩展（蓝图描述）

由于此功能依赖 C++ 接口，无法直接在蓝图中实现，但可以通过 C++ 模块创建后，在蓝图可调用的函数或编辑器工具中触发注册逻辑。典型流程是：
1.  创建一个 C++ 类继承自 `IShaderAuditExtension`。
2.  在该类构造函数或某个初始化函数中，调用 `IModularFeatures::Get().RegisterModularFeature(IShaderAuditExtension::FeatureName, this);` 进行注册。
3.  注册后，当用户打开或切换到 Shader Audit 会话视图时，你的扩展贡献的标签页和工具栏按钮会自动出现。

## C++ 用法

### 头文件引入

使用核心会话和类型系统：
```cpp
#include "ShaderAuditSession.h"
#include "ShaderAuditTypes.h"
#include "ShaderAuditViews.h"
```

使用着色器字节码数据库（如果需要分析字节码大小）：
```cpp
#include "ShaderBytecodeDatabase.h"
```

实现扩展接口：
```cpp
#include "IShaderAuditExtension.h"
```

### 基本用法：创建并填充审计会话

以下示例展示了如何加载 SHK 文件并构建一个审计会话的基础数据结构。来源文件：`Public/ShaderAuditSession.h`，`Public/ShaderAuditTypes.h`。

```cpp
#include "ShaderAuditSession.h"
#include "ShaderAuditTypes.h"

// 假设已获得一个 FShaderAuditSession 的共享指针，通常由 ShaderAudit 模块的内部工具创建
TSharedPtr<FShaderAuditSession> Session = MakeShared<FShaderAuditSession>();

// 模拟填充会话数据（实际中通常从 .shk 文件导入）
FShaderAuditSession::FStableShaderKeyAndValue Entry;
Entry.AssetName = TEXT("/Game/Materials/M_Master");
Entry.AssetPath = TEXT("/Game/Materials/M_Master");
Entry.ClassName = TEXT("Material");
Entry.ShaderType = TEXT("FDefaultMaterialVertexShader");
Entry.VFType = TEXT("FLocalVertexFactory");
Entry.PermutationId = 0;
Entry.OutputHash = FShaderHash::Create(TEXT("SomeHash")); // 模拟哈希

// 将条目添加到会话中
Session->StableShaderKeyAndValueArray.Add(Entry);

// 可以继续添加 UniqueMaterials 等其他数据...
```

### 进阶用法：使用过滤系统和构建视图

以下示例展示了如何使用过滤系统筛选着色器条目，并构建一个树状图视图数据。来源文件：`Public/ShaderAuditSession.h`， `Public/ShaderAuditViews.h`。

```cpp
#include "ShaderAuditSession.h"
#include "ShaderAuditViews.h"

// 假设 Session 已经填充了数据
TSharedPtr<FShaderAuditSession> Session = ...;

// 1. 定义过滤条件：只显示特定资产路径下的着色器
TArray<FShaderFilterNode> Filters;
FShaderFilterNode PathFilter;
PathFilter.Type = FShaderFilterNode::EType::Clause;
PathFilter.Field = EShaderFilterField::AssetPath;
PathFilter.Op = EShaderFilterOp::Contains;
PathFilter.Value = TEXT("/Game/Characters");
Filters.Add(PathFilter);

// 2. 构建可见性位数组，应用过滤
TBitArray<> VisibleShaders;
BuildVisibleShaders(*Session, Filters, /*MaxRefCount=*/0, VisibleShaders);

// 3. 使用过滤后的可见性数据，构建文件夹树状图
TMap<FString, TSharedPtr<FShaderFolderNode>> NodeMap;
TSharedRef<FShaderFolderNode> RootFolder = UE::ShaderAudit::BuildFolderTree(
    *Session,
    &VisibleShaders, // 传入过滤后的位数组
    NodeMap
);

// 现在 RootFolder 及其子节点只包含满足过滤条件的资产，且其 Cost 和 ShaderCount 仅反映可见着色器。
// 可以将此 RootFolder 传递给 SShaderCostTreeMap 进行渲染。

// 4. (可选) 构建用于 STreeMap 控件的数据
TSharedRef<FTreeMapNodeData> TreeMapData = UE::ShaderAudit::BuildTreeMapView(
    RootFolder,
    /*MaxDepth=*/3,
    /*bSizeWeighted=*/false
);
```

## Demo 示例

以下示例展示了如何创建一个最简的 `IShaderAuditExtension` 实现，为 Shader Audit 视图添加一个自定义标签页。

**MyShaderAuditExtension.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IShaderAuditExtension.h"

class FMyShaderAuditExtension : public IShaderAuditExtension
{
public:
    FMyShaderAuditExtension();
    virtual ~FMyShaderAuditExtension();

    // IShaderAuditExtension 接口
    virtual FName GetExtensionId() const override;
    virtual FText GetDisplayName() const override;
    virtual TArray<FShaderAuditExtensionContribution> GetContributions() const override;
    virtual void OnSessionLoaded(TSharedPtr<FShaderAuditSession> Session) override;

    // 注册和注销的辅助函数
    static void Register();
    static void Unregister();

private:
    // 示例：保存会话引用以供自定义 UI 使用
    TWeakPtr<FShaderAuditSession> CurrentSession;
};
```

**MyShaderAuditExtension.cpp**
```cpp
#include "MyShaderAuditExtension.h"
#include "Features/IModularFeatures.h"

#define LOCTEXT_NAMESPACE "FMyShaderAuditExtension"

FMyShaderAuditExtension::FMyShaderAuditExtension()
{
}

FMyShaderAuditExtension::~FMyShaderAuditExtension()
{
    Unregister();
}

FName FMyShaderAuditExtension::GetExtensionId() const
{
    // 返回一个唯一标识符
    return TEXT("MyCustomAuditView");
}

FText FMyShaderAuditExtension::GetDisplayName() const
{
    return LOCTEXT("ExtensionName", "My Custom Analysis");
}

TArray<FShaderAuditExtensionContribution> FMyShaderAuditExtension::GetContributions() const
{
    TArray<FShaderAuditExtensionContribution> Contributions;

    // 创建一个视图标签页贡献
    FShaderAuditExtensionContribution TabContribution;
    TabContribution.ViewTabLabel = LOCTEXT("CustomTabLabel", "Custom Stats");
    // 定义创建视图部件的工厂函数
    TabContribution.CreateViewWidget = [](TSharedPtr<FShaderAuditSession> Session) -> TSharedRef<SWidget>
    {
        // 这里可以返回你自定义的 Slate 控件，例如一个统计图表或列表
        // 示例：返回一个简单的文本块
        return SNew(STextBlock).Text(FText::Format(
            LOCTEXT("CustomViewText", "Custom view for session with {0} shaders."),
            FText::AsNumber(Session->StableShaderKeyAndValueArray.Num())
        ));
    };
    Contributions.Add(MoveTemp(TabContribution));

    // 可以添加更多贡献，例如工具栏按钮
    // FShaderAuditExtensionContribution ToolbarContribution;
    // ToolbarContribution.CreateToolbarWidget = [](TSharedPtr<FShaderAuditSession>) -> TSharedRef<SWidget> { ... };
    // Contributions.Add(ToolbarContribution);

    return Contributions;
}

void FMyShaderAuditExtension::OnSessionLoaded(TSharedPtr<FShaderAuditSession> Session)
{
    // 会话加载完成时的回调，可以保存引用或启动后台分析
    CurrentSession = Session;
}

void FMyShaderAuditExtension::Register()
{
    IModularFeatures::Get().RegisterModularFeature(FeatureName, Get());
}

void FMyShaderAuditExtension::Unregister()
{
    IModularFeatures::Get().UnregisterModularFeature(FeatureName, Get());
}

// 在你的模块启动时调用
void StartupModule()
{
    MyExtensionInstance = MakeShareable(new FMyShaderAuditExtension());
    MyExtensionInstance->Register();
}

// 在你的模块关闭时调用
void ShutdownModule()
{
    if (MyExtensionInstance.IsValid())
    {
        MyExtensionInstance->Unregister();
        MyExtensionInstance.Reset();
    }
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

从 `Build.cs` 文件分析，要使用此插件（特别是其核心库 `ShaderAuditCore`），你的模块需要链接以下依赖：

| 模块 | 用途 |
|---|---|
| `ShaderCodeLibrary` | 用于访问着色器代码库和字节码相关的类型（如 `FShaderHash`）。 |
| `MaterialValidation` | 插件声明的显式依赖，表明其功能与材质验证工具链相关。 |

此外，它还依赖标准的引擎模块如 `Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore` 等。

## 维护状态

### 近期更新

根据 Git 日志，此插件在 2026 年 5 月 12 日集中创建并提交了多个变更，目前处于初始开发阶段。

- 2026-05-12 `c4351fff` Create ShaderAuditCore module
  - 创建核心模块，建立基础架构。
- 2026-05-12 `0d38c80a` Create ShaderAuditCore module
  - 可能是对核心模块的进一步补充或重构。
- 2026-05-12 `d843e10b` ShaderAudit: Replace remaining inline #if WITH_EDITOR with slate event for material hierarchy fetch
  - 将编辑器特定代码替换为通过 Slate 事件委托，提高代码模块化和可测试性。
- 2026-05-12 `263d8b5e` Remove inline WITH_EDITOR in shaderaudit and instead use slate events that are setup from ShaderAudi
  - 与上一次提交类似，继续解耦编辑器依赖。

### 维护评价

- **年龄**：插件于 2026 年 5 月 12 日创建，属于**全新**插件。
- **活跃度**：在创建当日有密集的提交活动，表明正在积极初始开发中。所有提交都是实质性功能开发，而非简单的修复或文档更新。
- **状态**：标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，明确处于实验性阶段。
- **风险与限制**：作为实验性新插件，其 API 和功能在未来版本中可能发生重大变化或不稳定。不建议在生产项目的稳定版本中直接依赖。
- **推荐**：适合技术美术、图形程序员或工具开发者用于**研究、原型开发和内部工具集成**。可以关注其发展，待其达到稳定状态后再考虑更广泛的采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ShaderToolkit)
- [官方文档](https://docs.unrealengine.com/)（无特定文档链接）