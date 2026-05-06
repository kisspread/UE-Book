# NiagaraFluids

> Fluid simulation toolkit for Niagara

| 属性 | 值 |
|---|---|
| 中文名 | 流体模拟工具集 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Niagara 资源、数据接口、模块定义） |
| 模块 | `NiagaraFluids` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraFluids) | |

## 用途

该插件为 Unreal Engine 的 Niagara 粒子系统提供了基于网格的流体模拟能力。它不通过新增 C++ 类直接暴露给蓝图或 C++ 调用，而是以 **Niagara 模块（Modules）**、**数据接口（Data Interfaces）** 和预设资源（Content）的形式，将流体求解器（如 2D/3D 气体、FFT 求解器、浅水波）集成到 Niagara 生态中。

通过该插件，你可以在 Niagara 发射器中直接驱动烟雾、火焰、水流等流体效果，而无需编写低级别 GPU 计算代码。它解决了以下问题：

- 在 Niagara 中快速实现高速、高视觉质量的流体模拟
- 提供与现有粒子系统无缝衔接的流体求解器
- 降低流体特效的制作门槛，让艺术家和设计师能直接使用

## 使用场景

- **烟雾与火焰**：使用 2D 气体求解器模拟烟气、爆炸、火焰尾巴，结合 Niagara 粒子渲染
- **水流与波浪**：利用浅水波（Shallow Water）求解器模拟水面波纹、流体表面交互
- **奇幻或自然特效**：毒雾、魔法烟雾、海面效果等，不需要精确物理但需要视觉可信度
- **游戏内实时流体**：例如火焰喷射器的气流、爆炸冲击波的可视化

## 蓝图用法

该插件 **没有直接暴露任何蓝图可调用函数或蓝图类**。所有功能都是通过 Niagara 内容编辑器中的自定义模块和数据接口来使用。  
在 Niagara 编辑器中，你可以：

1. 创建新的 Niagara 系统或发射器
2. 在“Module”面板中搜索 `Fluid`、`FFT`、`ShallowWater` 等关键词
3. 将相关的流体模块拖入发射器的脚本中，并调整参数（如粘度、时间步长、网格分辨率等）

例如，一个常见的流程是：
- 添加 `Fluid Simulation` 模块（负责求解）
- 绑定 `Grid Data Interface` 作为流体状态缓冲区
- 使用 `Particle Attribute Reader` 从流体网格中采样颜色/速度，驱动粒子外观

因此，文档中无法列举具体的蓝图节点，但使用路径完全在 Niagara 编辑器中。

## C++ 用法

### 头文件引入

```cpp
#include "INiagaraFluids.h"
```

### 基本用法

通常你只需要通过模块接口访问插件是否加载，而不需要直接调用它的 API（因为流体功能均通过 Niagara 运行时系统自动执行）。示例：

```cpp
if (INiagaraFluids::IsAvailable())
{
    // 流体模拟插件已启用，可以安全地在 Niagara 中使用相关模块
    UE_LOG(LogTemp, Log, TEXT("NiagaraFluids module is loaded"));
}
```

该插件没有提供额外的 UCLASS 或 UFUNCTION，因此 C++ 侧主要用于确认模块可用性或在工具菜单中添加扩展（如编辑器入口）。

### 进阶用法

如果你需要在自定义计算中使用该插件的网格求解器，可以通过 Niagara 的 `UNiagaraDataInterface` 派生类进行交互。例如，从 C++ 中动态创建流体网格数据接口并驱动粒子行为。但这属于 Niagara 系统的高级用法，通常推荐在内容编辑器中完成。

## Demo 示例

由于插件核心功能在内容端，此处提供一个简单的模块加载检查示例。新建一个 C++ 类 `UMyFluidChecker`（继承自 `UObject`），在某个函数中检查插件是否可用。

**MyFluidChecker.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyFluidChecker.generated.h"

UCLASS(BlueprintType)
class UMyFluidChecker : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Fluid")
    bool IsNiagaraFluidsAvailable() const;
};
```

**MyFluidChecker.cpp**
```cpp
#include "MyFluidChecker.h"
#include "INiagaraFluids.h"

bool UMyFluidChecker::IsNiagaraFluidsAvailable() const
{
    return INiagaraFluids::IsAvailable();
}
```

> 注意：此示例仅用于演示如何引用模块，插件本身并未提供直接可供调用的流体模拟 API。实际流体逻辑均在 Niagara 运行时中执行。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 标准引擎核心 |
| `RenderCore` | GPU 计算和渲染资源管理（流体求解器需要） |
| `Projects` | 模块加载与插件管理 |
| `Niagara` | 必须依赖的 Niagara 插件（通过 .uplugin 声明的硬依赖） |

你的模块中若需使用 NiagaraFluids，需在 `PublicDependencyModuleNames` 中添加：
- `"NiagaraFluids"` —— 虽然主要功能在内容端，但为了安全获取 `INiagaraFluids` 接口仍需引用。

```cpp
PublicDependencyModuleNames.AddRange(new string[] { "NiagaraFluids" });
```

## 维护状态

### 近期更新

| 日期 | 提交 | 解读 |
|---|---|---|
| 2024-03-13 | `32e5d7e7` | 撤销并移除 `MatchSubstring` CoreRedirects 配置，改用通配符 |
| 2023-11-10 | `12d6a728` | [回退] 回退之前对 NiagarFluids 的更改 |
| 2023-11-09 | `d0d28d70` | 添加浅水波-水体集成（WIP） |
| 2023-09-18 | `2b0c75f0` | 暴露 2D 气体的 FFT 求解器 |
| 2023-02-16 | `f0b83454` | 清理模块直接包含 |

### 维护评价

- **创建时间**：2023 年 2 月，距今约 2 年。
- **更新频率**：最初几个月有功能更新（FFT 求解器、浅水波集成），之后进入长期维护阶段。2024 年仅有配置清理，未有新功能。
- **活跃度**：当前维护不活跃，最后一次实质性功能更新在 2023 年 11 月。
- **已知问题**：插件标记为 **Beta 版本**，意味着 API 和功能可能不稳定，且在 UE 5.7 中仍为实验性，默认不启用。可能缺少文档和示例资源。
- **推荐使用**：如果你需要快速在 Niagara 中实现简单的流体效果，它可以作为起点，但建议谨慎测试兼容性，并做好未来 API 变动的准备。对于生产级项目，可考虑更成熟的第三方流体解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraFluids)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/fluid-simulation-in-niagara/)（关联 Niagara 流体模拟文档，并非插件专属）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraFluids/Content)（插件内容资源目录）