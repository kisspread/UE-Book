# Chaos Solver

> Physics Solver（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 混沌求解器 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（图标资源） |
| 模块 | `ChaosSolverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosSolverPlugin) | |

## 用途

> 基于源码分析的实际功能，不照抄 Description。

Chaos Solver 插件为 **Chaos 物理系统** 提供了编辑器侧的资产管理和可视化支持。  
它允许用户创建 `UChaosSolver` 资产（用线框体即 AABB 简化表示），通过工厂在关卡中快速放置求解器 Actor，并提供属性面板的调试控制（暂停、单步、子步）。  
本质上这是一个**编辑器工具插件**，解决的是 Chaos 求解器参数的定制与调试需求，而实际物理计算仍由 Chaos 引擎模块执行。

## 使用场景

- 你在制作基于 Chaos 物理的模拟（破坏、布料、流体等），需要调整求解器迭代次数、子步数、容差等参数 —— 通过创建 Chaos Solver 资产并赋值给物理场景。
- 你需要直观地在关卡中放置一个 `ChaosSolver` Actor（线框表示），并通过细节面板实时调试求解器子步骤行为。

## 蓝图用法

> 此插件为纯编辑器代码，不暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 属性。  
> 因此蓝图侧无法直接调用该插件的 API，所有操作均在编辑器界面完成。

| 节点 | 说明 | 所在类 |
|---|---|---|
| **（无）** | 插件未暴露任何蓝图节点。 | - |

**编辑器操作流程**（蓝图无法使用，仅编辑器）：

1. 在内容浏览器右键 → "物理" → "Chaos Solver" 新建资产。
2. 双击资产打开编辑器（默认无专属窗口，仅显示属性）。
3. 将资产拖入场景生成 `AChaosSolverActor`（通过 `UActorFactoryChaosSolver`）。
4. 选择 Actor，在细节面板找到 "Debug Substep Controls" 展开，点击暂停/单步/子步按钮进行调试。

## C++ 用法

### 头文件引入

```cpp
#include "Chaos/ChaosSolverFactory.h"
#include "Chaos/AssetTypeActions_ChaosSolver.h"
```

### 基本用法

**通过工厂创建 Chaos Solver 资产**（C++ 中动态创建）

```cpp
// 文件：Source/ChaosSolverEditor/Private/Chaos/ChaosSolverFactory.cpp（推测）
UChaosSolver* NewSolver = UChaosSolverFactory::StaticFactoryCreateNew(
    UChaosSolver::StaticClass(),
    GetTransientPackage(),
    TEXT("MyChaosSolver"),
    RF_Transactional,
    nullptr,
    nullptr
);
```

**注册资产类型操作**（在模块启动时）：

```cpp
// 文件：Source/ChaosSolverEditor/Private/Chaos/ChaosSolverEditorPlugin.cpp
void IChaosSolverEditorPlugin::StartupModule()
{
    // 创建资产类型动作实例
    AssetTypeActions_ChaosSolver = new FAssetTypeActions_ChaosSolver();
    // 注册到资产工具模块（需包含 AssetTools.h）
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
    AssetTools.RegisterAssetTypeActions(MakeShareable(AssetTypeActions_ChaosSolver));
}
```

### 进阶用法

**自定义细节面板调试按钮**（用于暂停/步进求解器）

参考 `FChaosDebugSubstepControlCustomization`：

```cpp
// 文件：Source/ChaosSolverEditor/Private/Chaos/ChaosSolverEditorDetails.cpp
// 将自定义细节绑定到结构体属性
// 通常在模块的 StartupModule 中注册
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomPropertyTypeLayout(
    "ChaosDebugSubstepControl",
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FChaosDebugSubstepControlCustomization::MakeInstance)
);
```

**嵌入求解器到自定义 Actor 属性**：

```cpp
// 在你的 Actor 类中添加 UPROPERTY
UPROPERTY(EditAnywhere, Category = "Physics")
UChaosSolver* MyChaosSolver;
```

## Demo 示例

> 最小化演示：创建一个编辑器模块，加载 Chaos Solver 资产并添加到场景。

**MyChaosSolverDemo.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyChaosSolverDemo.generated.h"

class UChaosSolver;

UCLASS()
class AMyChaosSolverDemo : public AActor
{
    GENERATED_BODY()
public:
    AMyChaosSolverDemo();

    UPROPERTY(EditAnywhere, Category = "Physics")
    UChaosSolver* ChaosSolver;
};
```

**MyChaosSolverDemo.cpp**

```cpp
#include "MyChaosSolverDemo.h"
#include "Chaos/ChaosSolverFactory.h"  // 仅当需要动态创建时才需要

AMyChaosSolverDemo::AMyChaosSolverDemo()
{
    PrimaryActorTick.bCanEverTick = true;
    // 如果需要默认资产，可以在 BeginPlay 或构造函数中
    // 但推荐使用编辑器资产引用
}
```

**引擎示例**（在关卡中手动放置）：

1. 在内容浏览器创建 Chaos Solver 资产。
2. 将资产拖入关卡，自动生成 `AChaosSolverActor`（由 `UActorFactoryChaosSolver` 处理）。

## 模块依赖

> 省略常见依赖，只列出独特部分。

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理系统核心模块，提供 `UChaosSolver` 定义 |
| `AssetTools` | 注册资产类型操作 |
| `PropertyEditor` | 自定义细节面板 |

**说明**：由于 `UChaosSolver` 定义在 `Chaos` 模块内，因此 `ChaosSolverEditor` 必须依赖 `Chaos`。其他依赖如 `AssetTools`、`PropertyEditor` 为编辑器标准依赖，故不单独列出。完整依赖如下：

```cpp
// Source/ChaosSolverEditor/ChaosSolverEditor.Build.cs
PublicDependencyModuleNames.AddRange(new string[] { "Chaos", "AssetTools", "PropertyEditor" });
PrivateDependencyModuleNames.AddRange(new string[] { ... }); // 标准编辑器模块
```

## 维护状态

### 近期更新

| 日期 | Hash | 原始 Commit 说明 |
|---|---|---|
| 2025-05-31 | `52e3dac1` | 更新头文件 DLL 存储方法/静态变量（UnrealCodeFixup） |
| 2024-11-10 | `66e9bb39` | 移除所有 UE_INCLUDE_ORDER_DEPRECATED_IN_5_2 作用域 |
| 2023-11-15 | `b64f2e25` | [Deprecation Cleanup] 移除 Actor 工厂类中的弃用代码 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] 初始提交（批量处理） |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] 初始提交（批量处理） |

### 维护评价

- **创建时间**：2023-01-12（约 2.5 年前）。
- **更新频率**：创建后半年有一次清理，之后两年仅做编译兼容性修复（2024、2025 年的两次 commit 均为代码规范化）。
- **是否活跃**：不活跃。最近一次功能性更新是 2023-11-15 的弃用清理，再往后只有头文件调整。
- **已知问题**：插件标注为 Beta，功能尚不完善（例如资产编辑器无专属窗口）。无公开 issue。
- **推荐使用**：如果需要使用 Chaos 物理系统的求解器参数资产，可以启用该插件。但注意它是实验性 Beta 版本，可能在后续版本中移除或重构。对于新项目，建议直接使用 Chaos 物理系统自带的求解器参数结构体（如 `FSolverPropertyConfig`）替代资产方式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosSolverPlugin)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/chaos-physics-overview/)（Chaos 物理系统总览，未单独为该插件提供文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosSolverPlugin/Source/ChaosSolverEditor/Private)（暂无独立测试目录，核心代码位于 Private 文件夹）