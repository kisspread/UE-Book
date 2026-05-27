# VEUV - Volume Encoded UV Maps

> Volume encoded UV parameterization

| 属性 | 值 |
|---|---|
| 中文名 | 体积编码UV贴图 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `VEUVCore` (Runtime), `VEUVEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VEUV) | |

## 用途

VEUV 插件提供了一种实验性的 UV 参数化技术，其核心思路是将 UV 坐标编码到一个三维体积（Volume）内，而非传统的二维表面展开。这种方法可能用于处理复杂几何体或特定曲面上的 UV 展开问题，旨在减少传统 UV 展开中常见的拉伸和变形，或为特殊材质（如体积纹理、程序化纹理）提供更好的 UV 映射基础。它是一个正在开发中的实验性功能。

## 使用场景

-   **高质量角色资产制作**：当为角色皮肤、面部或精细部件生成 UV 时，可以尝试使用 VEUV 来最小化 UV 岛的变形，从而获得更高质量的纹理映射。
-   **复杂工业模型**：对于汽车、机械等包含大量光滑曲面的模型，VEUV 可能提供一种比传统展开更优的 UV 布局方案。
-   **程序化或体积化内容创作**：当需要将三维空间中的属性（如密度、梯度）映射到表面时，基于体积的编码方式可能更直观。

## 蓝图用法

VEUV 主要是一个编辑器和运行时技术模块，其蓝图接口可能集中在 `VEUVEditor` 模块提供的编辑器工具或自定义蓝图节点上。具体的 `BlueprintCallable` 函数用于在编辑器中执行 UV 计算或应用操作。详细 API 请参阅 [VEUVEditor 模块文档](VEUVEditor.md)。

### 使用示例（蓝图描述）

在编辑器中，你可能通过一个自定义的工具窗口或资产编辑器扩展来触发 VEUV 的计算。该过程可能涉及选择目标网格体，配置算法参数（如分辨率、迭代次数），然后执行计算，最终将生成的 UV 数据应用到网格体的指定 UV 通道上。

## C++ 用法

在 C++ 中，VEUV 的核心计算逻辑封装在 `VEUVCore` 模块中。你可以集成这些功能到自己的编辑器工具或运行时流程中。编辑器的集成和用户交互逻辑位于 `VEUVEditor` 模块。

### 头文件引入

```cpp
// 对于核心计算功能
#include "VEUVCoreModule.h"

// 对于编辑器集成
#include "VEUVEditorModule.h"
```

### 基本用法

从模块结构推断，你可能会使用 `VEUVCore` 提供的类来初始化一个 UV 参数化问题，并通过求解器来获取结果。

```cpp
// 概念性示例：使用 VEUVCore 进行 UV 参数化
// (具体类名和函数名需参考 VEUVCore.md)
#include "VEUVParameterization.h"

void ComputeVolumeEncodedUVs(UStaticMesh* Mesh)
{
    // 1. 初始化参数化对象
    FVEUVParameterization Param;
    Param.SetMesh(Mesh);

    // 2. 配置求解器参数
    Param.SetResolution(256);
    Param.SetIterations(100);

    // 3. 执行计算
    bool bSuccess = Param.Solve();

    // 4. 将结果应用到网格体的 UV 通道
    if (bSuccess)
    {
        Param.ApplyResults(Mesh, /* UV Channel */ 1);
    }
}
```

*（以上为概念性代码，实际 API 请参考模块文档）*

### 进阶用法

结合 `VEUVEditor` 模块，你可以创建自定义的编辑器工具窗口，为用户提供可视化的参数调整界面，并将计算任务异步化。

## Demo 示例

```cpp
// 文件: MyCustomVEUVTool.h
#pragma once
#include "EditorUtilityWidget.h"
#include "MyCustomVEUVTool.generated.h"

UCLASS(BlueprintType)
class UMyCustomVEUVTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    // 蓝图调用的函数，用于对选中的资产执行VEUV计算
    UFUNCTION(BlueprintCallable, Category = "VEUV")
    void RunVEUVOnSelectedAssets();
};
```

```cpp
// 文件: MyCustomVEUVTool.cpp
#include "MyCustomVEUVTool.h"
#include "VEUVEditorModule.h" // 可能包含工具函数
#include "AssetSelection.h"

void UMyCustomVEUVTool::RunVEUVOnSelectedAssets()
{
    TArray<UObject*> SelectedAssets = GetSelectedAssets();
    for (UObject* Asset : SelectedAssets)
    {
        if (UStaticMesh* StaticMesh = Cast<UStaticMesh>(Asset))
        {
            // 调用 VEUVEditor 模块提供的工具函数或直接使用 VEUVCore 进行计算
            // 示例：VEUVEditorTools::ApplyVolumeUVs(StaticMesh, Settings);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VEUVCore` | 提供核心的体积编码 UV 参数化算法和运行时数据结构。 |
| `VEUVEditor` | 提供编辑器内的工具、界面集成和资产操作功能。 |

## 维护状态

### 近期更新

```
- 2026-05-14 5d715960 Volume Encoded UVs, temporarily disabled injectivity term and moved to dense initial R78 solve
- 2026-05-13 df17886a VEUV: fail out with an empty chart rather than crash if the grid ends up with nothing allocated
- 2026-05-12 e76e4ca8 Volume Encoded UVs, disabled forced injectivity on refinement (too prone to exploding)
- 2026-05-12 cd2e1403 VEUV: add failure reporting -- detect failed packing, empty charts, inf/nan entries, inverted tris
- 2026-05-12 34b3773a VEUV: distribute complexity sample budget remainder across bins so low-budget voxels are not silently
```

### 维护评价

VEUV 是一个 **全新且活跃开发中** 的实验性插件（创建于 2026-05-12）。从最近的提交历史看，开发者正在密集地调整算法核心（如禁用某些容易出错的约束项、改进求解器初始化、增加鲁棒性和错误处理），这表明插件正处于功能开发和调试的关键阶段。

由于其 **实验性** (`IsExperimentalVersion: true`) 且 **未默认启用** (`EnabledByDefault: false`) 的状态，它尚未达到稳定生产可用的状态。API 和功能在短期内可能发生显著变化，且可能存在未知问题或限制。

**建议**：适合开发者、研究人员或技术美术进行实验和概念验证，**不推荐直接用于重要项目的生产流程**。建议密切关注后续更新日志以了解功能稳定化进程。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VEUV)
- [官方文档]() (暂无)
- [测试用例]() (路径待确认)