# NiagaraFluids

> Fluid simulation toolkit for Niagara（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Niagara流体模拟 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Niagara资产、流体模拟相关模块/预设） |
| 模块 | `NiagaraFluids` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraFluids) | |

## 用途

该插件为 Niagara 粒子系统提供了一套流体模拟的工具集和实现。它并非一个独立的物理模拟系统，而是作为 Niagara 框架的一个扩展模块，旨在让开发者和艺术家能够利用 Niagara 编辑器来创建和模拟复杂的流体效果，如火焰、烟雾、水流等。其核心在于为 Niagara 的 Data Interface 和模块化节点提供底层的流体模拟算法支持。

## 使用场景

-   当你需要使用 Niagara 创建高度逼真、动态交互的烟雾、火焰或蒸汽效果时。
-   当你需要模拟基于网格的 2D/3D 流体（如气体、浅水）并希望将其无缝集成到现有的 Niagara 粒子管线中时。
-   当你希望避免使用独立的物理流体解决方案（如 NVIDIA FleX），而倾向于使用 UE 原生的、与引擎渲染管线深度集成的流体模拟方案时。

## 蓝图用法

根据源码分析，`NiagaraFluids` 模块本身主要提供模块接口和运行时支持，**没有直接暴露供蓝图调用的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性**。该插件的功能主要通过 **Niagara 编辑器** 暴露。

### 核心交互方式

该插件的功能在蓝图层面主要体现在 Niagara 系统和发射器的**模块化节点**上。使用者无需直接操作蓝图函数，而是在 Niagara 编辑器中：

1.  创建或打开一个 Niagara System。
2.  在发射器的“更新”或“生成”阶段，通过“+”号添加模块。
3.  在模块列表中，筛选或查找由 NiagaraFluids 插件提供的流体模拟相关模块（例如，“Fluid”、“Gas”、“Water”等分类下的模块）。
4.  配置这些模块的参数（如密度、粘度、涡流强度等）。

### 使用示例（Niagara 编辑器描述）

1.  打开 Niagara 编辑器，创建一个新的 Niagara System。
2.  在发射器的 “Emitter Update” 阶段，点击 “+” -> “Add from Plugin Modules” -> “FluidSimulation”（具体名称可能根据版本变化）。
3.  添加如 “Solve Fluid” 或 “Advect Particles” 等模块。
4.  在模块的细节面板中，调整 “Grid Resolution”、“Diffusion”、“Vorticity” 等属性。
5.  在粒子属性映射模块中，将流体模拟产生的速度场等数据映射到粒子的位置或速度上。

## C++ 用法

插件提供的 C++ 接口主要用于模块的加载与检查。

### 头文件引入

```cpp
#include "INiagaraFluids.h"
```

### 基本用法

主要用于在代码中检查 Niagara 流体模拟模块是否已加载并可用。

```cpp
// 来源：Source/NiagaraFluids/Public/INiagaraFluids.h

// 检查模块是否可用
if (INiagaraFluids::IsAvailable())
{
    // 获取模块实例，用于后续可能的初始化或配置调用
    INiagaraFluids& NiagaraFluidsModule = INiagaraFluids::Get();
    // 当前模块接口未定义额外公共方法，此引用主要用于确认模块加载状态。
}
```

### 进阶用法

该插件的进阶 C++ 用法通常不直接使用 `INiagaraFluids` 接口。更复杂的集成涉及：

1.  **开发自定义的 Niagara 模块**：这些模块内部使用 NiagaraFluids 插件提供的底层函数库和类来执行流体计算。
2.  **创建自定义 Data Interface**：用于在 Niagara 和外部流体求解器（可能是该插件提供的）之间高效传输数据。

由于提供的源码仅包含模块接口，具体的计算逻辑封装在其他未显示的文件或依赖模块（如 Niagara 本身）中。

## Demo 示例

由于此插件主要通过 Niagara 编辑器使用，C++ Demo 主要展示模块加载。一个使用 Niagara 编辑器创建流体模拟效果的最小化描述如下：

1.  **启用插件**：在项目设置或插件管理器中启用 “NiagaraFluids”。
2.  **创建资产**：在内容浏览器中右键 -> FX -> Niagara System -> 新建一个空的 Niagara System。
3.  **配置发射器**：打开该系统，在发射器的 “Emitter Update” 阶段，搜索并添加一个由 NiagaraFluids 提供的模块，例如 “Simple Gas Solver”。
4.  **连接输出**：在发射器的 “Particle Update” 阶段，添加 “Sprite Renderer”，并确保粒子的 “Position” 属性通过 Niagara 的 “Attribute Set” 与流体求解器的输出相连。
5.  **拖入场景**：将此 Niagara System 拖入场景中，即可观察到由流体模拟驱动的粒子效果（如烟雾）。

## 模块依赖

从 `Build.cs` 文件分析，此插件依赖关系非常基础。

| 模块 | 用途 |
|---|---|
| `RenderCore` | 提供渲染核心功能，可能用于流体数据的 GPU 计算和资源管理。 |

（无其他特殊依赖，仅依赖标准 Core、Projects 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件名从 Base 统一改为 Default，属于引擎标准化维护。 |
| 2024-03-13 | `32e5d7e7` | Deprecates and removes MatchSubstring CoreRedirects from ini files in favour of `MatchWildcard=true, | 弃用旧的 INI 重定向方式，采用新的通配符匹配，是配置系统清理工作的一部分。 |
| 2023-11-10 | `12d6a728` | [Backout] - CL29603921 | 回退了之前的某项改动，可能与浅水集成的稳定性有关。 |
| 2023-11-09 | `d0d28d70` | NiagaraFluids: Add ShallowWater-WaterBody integration WIP | 为浅水模拟添加与引擎 WaterBody 系统的集成（工作进行中），是功能扩展。 |
| 2023-09-18 | `2b0c75f0` | Expose FFT solver for 2D gases | 暴露了用于 2D 气体模拟的 FFT（快速傅里叶变换）求解器，增强了气体模拟能力。 |

### 维护评价

-   **创建时间**：约 4 年前创建。
-   **近期活动**：最近一次提交在 2025 年 10 月，属于常规维护。2023 年末至 2024 年初有明确的**功能更新**（浅水集成、FFT 求解器暴露）。
-   **状态评估**：**维护中**。虽然提交频率不高，但近期（一年内）有实质性功能添加和维护性更新，表明插件仍在 Epic 的维护范围内，且处于 Beta 状态意味着功能可能还会调整或完善。
-   **推荐**：对于需要在 Niagara 中使用原生流体模拟的项目，特别是已接受其 Beta 状态的开发者，此插件是一个值得尝试的选择。使用者应关注其 Beta 版本可能带来的 API 变动和稳定性风险。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraFluids)
-   [官方文档]()（无）
-   [测试用例]()（未在源码中发现明确的测试文件）