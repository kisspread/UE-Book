# Wave Function Collapse (Experimental)

> Wave Function Collapse tools for tile-based model synthesis

| 属性 | 值 |
|---|---|
| 中文名 | 波函数坍缩 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WaveFunctionCollapse` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WaveFunctionCollapse) | |

## 用途

插件实现了经典的**波函数坍缩（WFC）算法**，用于编辑器内的基于瓦片的程序化内容生成。由用户定义一组“选项”（如 StaticMesh 或蓝图 actor）及其安置规则（邻居约束与权重），插件通过迭代式的 Observation-Propagation 过程在 3D 网格上生成一个无矛盾的布局，并最终将结果实例化为实际 Actor。适用于快速原型、关卡白模搭建、自然地形或建筑物排列等需要从少量输入自动产生丰富变化的场景。

## 使用场景

- 你需要为一个关卡快速生成地板、墙壁和屋顶的布局 → 定义网格分辨率、选项（不同 tiles）和邻居约束，一键生成
- 你是关卡设计师，希望从简单的规则库产生多样化的室内布局 → 使用该插件迭代求解并预览结果
- 你在研究程序化生成算法，需要一个可直接在 UE 编辑器中运行的 WFC 实现 → 直接调用蓝图函数库或在 C++ 中使用 `UWaveFunctionCollapseSubsystem`

## 蓝图用法

插件提供了蓝图函数库 `UWaveFunctionCollapseBPLibrary` 和编辑器子系统 `UWaveFunctionCollapseSubsystem`。核心操作是：准备模型 → 运行 `Collapse`（求解并生成）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Collapse` | 使用当前设置的 `WFCModel`、`Resolution` 等参数执行 WFC 求解，成功则生成 Actor 并返回 | `UWaveFunctionCollapseSubsystem` |
| `InitializeWFC` | 初始化 Tile 数组和 RemainingTiles 数组，包含起始选项和边界处理（用户可手动进行多步控制） | `UWaveFunctionCollapseSubsystem` |
| `Observe` | 观察阶段：从最小熵的 Tile 中随机选择一个有效选项 | `UWaveFunctionCollapseSubsystem` |
| `Propagate` | 传播阶段：根据选中选项约束相邻 Tile 的剩余选项，返回是否矛盾 | `UWaveFunctionCollapseSubsystem` |
| `CalculateShannonEntropy` | 根据模型权重计算选项数组的香农熵（用于选择最小熵 Tile） | `UWaveFunctionCollapseBPLibrary` |
| `PositionAsIndex` / `IndexAsPosition` | 在 3D 网格坐标与扁平数组索引之间转换 | `UWaveFunctionCollapseBPLibrary` |

### 使用示例（蓝图描述）

1. **一步生成**：在关卡蓝图中获取 `WaveFunctionCollapseSubsystem`（编辑器子系统） → 设置其 `WFCModel` 为已创建的数据资产 → 设置 `Resolution` (例如 `(5,5,1)`) → 调用 `Collapse(TryCount=10)`，输出为生成的 Actor。
2. **分步控制**：先调用 `InitializeWFC` 获取 `Tiles` 和 `RemainingTiles` → 循环调用 `Observe` 和 `Propagate` 直到所有 Tile 坍缩或矛盾发生 → 若成功则根据最终选项生成 Actor。

## C++ 用法

### 头文件引入

```cpp
#include "WaveFunctionCollapseSubsystem.h"
#include "WaveFunctionCollapseModel.h"
```

### 基本用法

从 `UWaveFunctionCollapseSubsystem` 的测试用例（未提供，根据 API 推导）出发，创建模型和子系统进行求解：

```cpp
// 假设你在一个编辑器模块中运行
UWaveFunctionCollapseSubsystem* WFCSubsystem = GEditor->GetEditorSubsystem<UWaveFunctionCollapseSubsystem>();

// 设置模型 (从内容浏览器加载或创建)
UWaveFunctionCollapseModel* Model = NewObject<UWaveFunctionCollapseModel>();
Model->SetFlags(RF_Public | RF_Standalone);
// ... 向 Model 添加 Options 和约束规则 ...

WFCSubsystem->WFCModel = Model;
WFCSubsystem->Resolution = FIntVector(5, 5, 1);
WFCSubsystem->OriginLocation = FVector::ZeroVector;

// 执行求解 (尝试 10 次直到成功)
AActor* Result = WFCSubsystem->Collapse(10, 0);
if (Result)
{
    UE_LOG(LogWFC, Log, TEXT("WFC 成功生成 Actor: %s"), *Result->GetName());
}
```

来源文件: `Engine/Plugins/Experimental/WaveFunctionCollapse/Source/WaveFunctionCollapse/Public/WaveFunctionCollapseSubsystem.h`

### 进阶用法

手动控制 Observation-Propagation 循环以实现自定义逻辑（如暂停重试、记录中间状态）：

```cpp
TArray<FWaveFunctionCollapseTile> Tiles;
TArray<int32> RemainingTiles;
TMap<int32, FWaveFunctionCollapseQueueElement> ObservationQueue;

WFCSubsystem->InitializeWFC(Tiles, RemainingTiles);

int32 PropagationCount = 0;
bool bSolved = false;
for (int32 Attempt = 0; Attempt < 10; Attempt++)
{
    // 执行观察
    if (!WFCSubsystem->Observe(Tiles, RemainingTiles, ObservationQueue, FMath::Rand()))
        continue;

    // 传播约束
    if (!WFCSubsystem->Propagate(Tiles, RemainingTiles, ObservationQueue, PropagationCount))
        continue;

    // 检查是否所有 Tile 都已坍缩
    // 实际逻辑需要遍历 Tiles 判断 FWaveFunctionCollapseTile.IsCollapsed()
    // ... 从源码: FWaveFunctionCollapseTile 有 IsCollapsed() 方法
    bSolved = true;
    for (auto& Tile : Tiles)
    {
        if (!Tile.IsCollapsed())
        {
            bSolved = false;
            break;
        }
    }
    if (bSolved) break;
}

// 成功则生成 Actor
if (bSolved)
{
    AActor* Spawned = WFCSubsystem->CollapseSingleResult(Tiles); // 假设存在此函数
}
```

来源: 综合 `Collapse` 源码逻辑。

## Demo 示例

以下是一个最小 C++ 模块示例，展示如何创建 WFC 模型并执行求解（需在 Editor-only 模块中运行）：

```cpp
// MyWFCExample.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyWFCExampleModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyWFCExample.cpp
#include "MyWFCExample.h"
#include "WaveFunctionCollapseSubsystem.h"
#include "WaveFunctionCollapseModel.h"
#include "EngineUtils.h"
#include "Editor.h"

IMPLEMENT_MODULE(FMyWFCExampleModule, MyWFCExample);

void FMyWFCExampleModule::StartupModule()
{
    // 在编辑器启动后执行（可通过 Timer 或菜单调用）
    UWaveFunctionCollapseSubsystem* WFC = GEditor->GetEditorSubsystem<UWaveFunctionCollapseSubsystem>();
    if (!WFC) return;

    // 创建模型（至少需要添加一些选项）
    UWaveFunctionCollapseModel* Model = NewObject<UWaveFunctionCollapseModel>(GetTransientPackage());
    Model->AddUniqueOption(FWaveFunctionCollapseOption(TEXT("/Game/MyAssets/SM_Wall.SM_Wall")));
    Model->AddConstraint(... // 添加邻居规则
    WFC->WFCModel = Model;
    WFC->Resolution = FIntVector(3,3,1);
    WFC->OriginLocation = FVector(0,0,0);
    WFC->bUseEmptyBorder = true;

    AActor* Result = WFC->Collapse(50, 0);
    if (Result)
    {
        UE_LOG(LogTemp, Log, TEXT("WFC Example: Generated %s"), *Result->GetName());
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。`UEditorSubsystem` 需要 `UnrealEd` 模块，但属于编辑器插件常见依赖，按规范省略。

| 模块 | 用途 |
|---|---|
| （无独特依赖） | |

## 维护状态

### 近期更新

| 日期 | Commit | 解读 |
|---|---|---|
| 2025-05-12 | 869e8f18 | 修复元数据中的短路径/错误名称 |
| 2025-03-19 | 2596d96b | 支持蓝图中使用波函数坍缩的生成类 |
| 2024-01-25 | f43fc1d7 | 修复 bool 调用以适应 EAllowShrinking |
| 2023-02-27 | 5f370d9b | 修复日志宏重构引发的静态分析警告 |
| 2023-01-16 | bbc37aa2 | 初始提交（插件创建） |

### 维护评价

创建于 2023 年初，至今约 2.7 年，仍处于“实验性”阶段。近半年内（2025-03）有功能性更新（支持蓝图生成类），表明团队在持续改进。未发现废弃标记或已知严重问题。对于需要程序化生成的团队，该插件已提供完整的 WFC 核心功能，推荐在实验性项目中试用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WaveFunctionCollapse)