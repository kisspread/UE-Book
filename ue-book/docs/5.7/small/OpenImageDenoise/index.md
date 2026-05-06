# OpenImageDenoise

> Denoising engine for the Unreal Path Tracer based on Intel's OpenImageDenoise library.

| 属性 | 值 |
|---|---|
| 中文名 | 图像降噪 |
| 分类 | Denoising |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OpenImageDenoise` (ClientOnly) |
| 实验性 | 否 |
| 创建时间 | 2024-07-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OpenImageDenoise) | |

## 用途

该插件基于 Intel 开源的 OpenImageDenoise 库，为 Unreal Engine 的路径追踪器（Path Tracer）提供硬件加速的图像降噪功能。路径追踪渲染会产生大量随机噪点，尤其在高采样次数不足时。OpenImageDenoise 利用深度学习模型对渲染结果进行实时或离线的降噪处理，在保持细节的同时显著减少噪点，大幅提升画面质量。

插件本身不提供 UI 或额外蓝图节点——启用后自动嵌入路径追踪器的后处理流程。适用于需要极高渲染质量的场景，例如建筑可视化、产品展示、电影级预览等。

## 使用场景

- **离线渲染**：在不增加采样次数的情况下，通过降噪获得干净图像，缩短渲染时间。
- **实时预览**：配合路径追踪器在编辑器中交互查看最终效果，减少视觉噪声。
- **多帧序列**：对动画帧进行批量降噪，保持时间一致性。

## 蓝图用法

该插件完全工作在引擎底层，没有暴露任何可用于蓝图的函数或属性。路径追踪器相关的降噪选项可在 **项目设置 → 渲染 → 路径追踪器** 中找到（启用插件后会出现）。这些设置通常通过 C++ 或控制台变量访问，而非蓝图。

## C++ 用法

插件主要与路径追踪器渲染模块交互，开发者通常无需直接调用。但可以通过控制台变量或项目设置进行配置。

### 头文件引入

```cpp
#include "IOpenImageDenoiseModule.h"   // 如果暴露接口
```

### 基本用法

启用插件后，降噪自动应用于路径追踪器的最终输出。要调整降噪强度或开关，可用以下控制台变量：

- `r.PathTracing.Denoise` (bool) – 启用/禁用降噪 (1/0)
- `r.PathTracing.Denoise.Alpha` (bool) – 是否对 Alpha 通道降噪（从 git 记录推断）

在 C++ 中可通过 `IConsoleManager` 访问：

```cpp
static TAutoConsoleVariable<int32> CVarDenoise(
    TEXT("r.PathTracing.Denoise"),
    1,
    TEXT("Enable OpenImageDenoise for Path Tracer (0=off, 1=on)"));
```

> 以上变量属推测，实际请参考头文件 `Engine/Source/Runtime/Renderer/Private/PathTracing/...`。

### 进阶用法

可通过自定义渲染管道集成 OpenImageDenoise。但通常路径追踪器已内置支持。若需扩展，可参考 `IOpenImageDenoiseModule` 接口（如果存在）。

```cpp
if (IOpenImageDenoiseModule* DenoiseModule = FModuleManager::GetModulePtr<IOpenImageDenoiseModule>("OpenImageDenoise"))
{
    DenoiseModule->SetDenoiseParams(...);
}
```

> 注：以上代码为假设，具体 API 请以实际头文件为准。

## Demo 示例

由于插件为纯基础设施，无公开测试用例，此处提供一个最小 C++ 示例展示如何在运行时检查降噪是否启用：

**MyActor.h**:
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
};
```

**MyActor.cpp**:
```cpp
#include "MyActor.h"
#include "Misc/ConsoleManager.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 检查降噪是否启用
    IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("r.PathTracing.Denoise"));
    if (CVar && CVar->GetInt() == 1)
    {
        UE_LOG(LogTemp, Log, TEXT("OpenImageDenoise is active."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("OpenImageDenoise is disabled."));
    }
}
```

> 实际使用时需确保项目已启用该插件，且使用路径追踪器渲染模式。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MessageLog` | 输出降噪过程中的调试信息和日志 |

其余依赖均为标准引擎模块（Core, CoreUObject, Engine 等），此处省略。

## 维护状态

### 近期更新

- 2025-06-03 `0a44e4b8` — 支持按架构包含/排除插件模块（适配 ARM64）
- 2025-01-15 `d190c59c` — 修复 Windows Arm64 相关问题
- 2024-12-06 `d439e46e` — 修复 Alpha 通道降噪
- 2024-09-24 `123303b0` — 默认禁用插件（避免影响非路径追踪项目）
- 2024-07-17 `8f2f33a5` — 将辐射缓冲改回 32 位精度（初始提交）

### 维护评价

从提交历史看，插件自 2024 年 7 月创建后持续有修复与功能调整，最近一次更新在 2025 年 6 月，维护较为活跃。虽然目录位于 Experimental，但官方已将其视为可使用的工具，且修复了多个实际问题。对于需要使用路径追踪器的高质量渲染项目，推荐启用此插件。

**已知限制**：
- 仅支持 Win64 (x64) 平台，不支持 ARM64。
- 作为实验性插件，API 可能在未来版本变更。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OpenImageDenoise)
- [Intel OpenImageDenoise 官方文档](https://openimagedenoise.github.io/documentation/)
- [路径追踪器文档](https://docs.unrealengine.com/5.4/en-US/path-tracer-in-unreal-engine/)