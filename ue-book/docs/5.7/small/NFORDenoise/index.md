# NFORDenoise

> Spatial-temporal denoising engine for the Unreal Path Tracer (mainly used with MRQ). It denoises each pixel based on the surrounding patches in space and time in all directions. The algorithm is mainly inspired by Nonlinearly Weighted First-order Regression (NFOR) for Denoising Monte Carlo Renderings.

| 属性 | 值 |
|---|---|
| 中文名 | NFOR 去噪引擎 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `NFORDenoise` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NFORDenoise) | |

## 用途

NFORDenoise 是一个专为 Unreal 路径追踪器（Path Tracer）设计的高质量时空去噪引擎，主要配合 Movie Render Queue (MRQ) 使用。它基于 **非线性加权一阶回归（NFOR）** 算法，对蒙特卡洛渲染结果中的噪声进行滤波：每个像素根据其周围（空间和时间维度）的 patches 进行加权回归，从而在保留细节的同时显著降低噪声。

该插件解决了路径追踪渲染中常见的噪声问题，使得 MRQ 可以在更少的采样数下输出干净的帧，大幅缩短渲染时间，同时保持优秀的图像质量。

## 使用场景

- 使用 MRQ 进行电影级离线渲染，需要快速去噪以减少渲染时间。
- 在交互式预览中，希望看到低采样数的干净预渲染结果。
- 需要高质量去噪以控制最终成片的噪点水平，同时避免模糊细节。

## 蓝图用法

**无公开蓝图 API。**  
该插件完全集成在渲染管线中，作为后处理自动生效，无需手动调用任何蓝图节点。所有控制通过控制台变量（Console Variables）完成，详见“C++ 用法”中的控制台变量列表。

## C++ 用法

插件提供少量 C++ 实用函数，主要用于查询帧信息，但仍以自动集成为主。

### 头文件引入

```cpp
#include "NFORDenoise/Public/NFORDenoise.h"
```

### 基本用法

不推荐外部代码直接调用内部着色器或求解器。如需获取当前去噪帧索引，可以使用：

```cpp
const FSceneView& View = ...;
int32 FrameIndex = NFORDenoise::GetDenoisingFrameIndex(View, -1);  // -1 表示自动使用默认缓冲帧数
int32 FrameCount  = NFORDenoise::GetFrameCount(View);
```

这些函数定义在 `NFORDenoise.h` 中（位于 `NFORDenoise` 命名空间）。

### 控制台变量

以下控制台变量可在运行中调整去噪参数（示例）：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `r.NFORDenoise.PreAlbedoDivideOffset` | 0.1 | 控制材质的预倒数除偏移量，避免除零，默认0.1。 |

这些变量在插件初始化时自动注册，可在 `ConsoleVariables.ini` 或命令行中修改。

## Demo 示例

无需编写代码。在项目中启用插件后，使用 MRQ 设置路径追踪渲染器，即可自动获得去噪结果。

若要验证插件是否生效，可打开控制台输入 `r.NFORDenoise 1` 启用，或查看渲染输出中噪点是否明显减少。

## 模块依赖

无特殊依赖（仅标准 Engine/RenderCore/RHI 等）。

| 模块 | 用途 |
|------|------|
| （无） | 插件自带全部依赖，无需额外添加。 |

如果项目需要引用 `NFORDenoise` 模块中的符号（如 `NFORDenoise::GetFrameCount`），则需在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "NFORDenoise" });
```

## 维护状态

### 近期更新

- 2025-04-24 `0276eca4` — [PathTracing] 按需输出方差而非始终捕获，降低默认开销。
- 2024-09-16 `3eb437e9` — 将预面积除偏移改为 0.1 以获得更平滑的 NFOR 去噪默认效果。
- 2024-09-03 `3d4416bc` — 修复 NFOR 去噪器中法线未按向量长度缩放的问题。
- 2024-08-13 `1bd8eeb8` — 回退到更稳定的线性求解器，直到快速求解器的鲁棒性得到改善。
- 2024-08-05 `d77e3ada` — 为 NFOR 内部去噪纹理缓冲区添加格式类型检查。

### 维护评价

- **创建时间**：2024-08-05（约 1 年）
- **更新频率**：持续活跃，最近一次功能性更新在 2025-04-24
- **当前状态**：维护中，Epic Games 持续根据用户反馈优化去噪质量和性能
- **推荐度**：✅ 推荐用于 MRQ 路径追踪渲染。当前仍标为“实验性”（IsExperimentalVersion=true），但功能已较为完善，适合生产使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NFORDenoise)
- [官方文档](https：//docs.unrealengine.com/5.7/en-US/path-tracer-denoiser/)（如已发布）
- [控制台变量参考](https：//docs.unrealengine.com/5.7/en-US/console-variables-in-unreal-engine/)（搜索“NFORDenoise”）