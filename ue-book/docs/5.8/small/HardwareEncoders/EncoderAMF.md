# Hardware Encoders

> Adds support of hardware encoders to AVEncoder

| 属性 | 值 |
|---|---|
| 中文名 | 硬件编码器 |
| 分类 | Encoders |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无（纯代码插件） |
| 模块 | `EncoderAMF` (Runtime), `EncoderNVENC` (Runtime) |
| 实验性 | ⚦️ 是（Beta版本） |
| 创建时间 | 2021-10-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HardwareEncoders) | |

## 用途

该插件是 UE5 中 `AVEncoder` 框架的扩展，旨在为其添加对特定 GPU 硬件编码器的支持。它本身不提供独立的编码功能，而是作为插件模块，将 AMD AMF 和 NVIDIA NVENC 等底层硬件编码器 API 集成到引擎的视频编码系统（AVEncoder）中。

**核心解决的问题**：在需要进行实时视频编码（例如 Pixel Streaming、录制或直播）的场景中，仅依赖 CPU 软件编码（如 libvpx）性能开销巨大。此插件通过利用 GPU 的专用硬件编码单元，可以显著降低 CPU 负载，提升编码效率和质量，是构建高性能实时视频流媒体功能的基础设施。

## 使用场景

- **云游戏/云渲染 (Pixel Streaming)**：在服务器端为每一位玩家或渲染实例进行实时的、低延迟的视频流编码。
- **视频会议与直播应用**：在客户端或服务器端进行高效的屏幕共享或摄像头视频流编码。
- **游戏内录像**：以较低的性能损耗录制高分辨率的游戏画面。
- **任何依赖 `AVEncoder` 进行实时视频编码的自定义功能**。

## 蓝图用法

此插件主要为 C++ 层面的 `AVEncoder` 系统提供底层硬件编码器支持，不直接暴露蓝图节点。其功能通过 `AVEncoder` 的上层接口间接使用。若要在蓝图中使用视频编码功能，应关注 `AVEncoder` 模块本身提供的蓝图接口。

## C++ 用法

### 头文件引入

此插件的核心类为内部实现，不应被直接包含。集成和使用时，应通过 `AVEncoder` 模块的公共接口。

```cpp
// 通常需要包含 AVEncoder 的头文件来使用编码功能
#include "AVEncoder.h"
// 或根据具体功能需要包含特定头文件
```

### 基本用法

插件的核心作用是向 `AVEncoder` 的工厂注册硬件编码器。使用者无需直接与插件中的 `FVideoEncoderAmf_H264` 或 NVENC 类交互。以下为插件内部注册逻辑的简化示意：

```cpp
// 来自源码推断（非直接复制文件）
// 在合适的初始化时机，插件会调用类似以下逻辑将自身编码器注册到工厂
void FVideoEncoderAmf_H264::Register(FVideoEncoderFactory& InFactory)
{
    // 检查当前系统是否支持此硬件编码器
    if (FVideoEncoderAmf_H264::GetIsAvailable(/* input */, /* encoderInfo */))
    {
        // 将创建 H264 AMF 编码器实例的函数注册到工厂
        InFactory.RegisterEncoder(/* 编码器标识符 */, []() -> TSharedPtr<FVideoEncoder> {
            return MakeShareable(new FVideoEncoderAmf_H264());
        });
    }
}
```

**使用者集成**：作为插件使用者，当你的模块需要视频编码功能时，只需依赖 `AVEncoder` 模块，并通过 `FVideoEncoderFactory` 请求一个合适的编码器即可。`AVEncoder` 会自动加载已启用的硬件编码器插件（如本插件）并选择最优的硬件编码器。

### 进阶用法

1.  **查询编码器可用性**：
    在尝试创建编码器前，可以查询特定硬件编码器是否在当前系统可用。这通常在 `AVEncoder` 内部或通过 `FVideoEncoderInfo` 完成。

2.  **配置编码参数**：
    通过 `AVEncoder` 的 `FEncodeOptions` 和 `FLayerConfig` 结构体来设置目标比特率、分辨率、帧率、关键帧间隔等。硬件编码器插件会将其转换为对应的硬件 API 调用（如 AMF 的属性设置）。

## Demo 示例

以下是一个概念性的示例，展示如何通过 `AVEncoder` 框架使用一个已注册的硬件编码器进行编码。

```cpp
// MyVideoEncoderManager.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyVideoEncoderManager.generated.h"

class AVEncoder::FVideoEncoder;
class AVEncoder::FVideoEncoderInput;
class AVEncoder::FVideoEncoderFactory;

UCLASS()
class UMyVideoEncoderManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // 开始一个编码会话
    UFUNCTION(BlueprintCallable, Category = "Video Encoding")
    bool StartEncoding(int32 Width, int32 Height, int32 Framerate);

    // 提交一帧进行编码
    UFUNCTION(BlueprintCallable, Category = "Video Encoding")
    void SubmitFrame(const TArray<FColor>& FrameData);

    // 停止编码
    UFUNCTION(BlueprintCallable, Category = "Video Encoding")
    void StopEncoding();

private:
    TSharedPtr<AVEncoder::FVideoEncoder> ActiveEncoder;
    TSharedPtr<AVEncoder::FVideoEncoderInput> EncoderInput;
};
```

```cpp
// MyVideoEncoderManager.cpp
#include "MyVideoEncoderManager.h"
// 包含 AVEncoder 的头文件
#include "AVEncoder.h"

void UMyVideoEncoderManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 确保 AVEncoder 子系统已初始化
    // AVEncoder 子系统会自动加载和注册像 HardwareEncoders 这样的插件
}

void UMyVideoEncoderManager::Deinitialize()
{
    StopEncoding();
    Super::Deinitialize();
}

bool UMyVideoEncoderManager::StartEncoding(int32 Width, int32 Height, int32 Framerate)
{
    if (ActiveEncoder.IsValid())
    {
        StopEncoding();
    }

    // 获取全局的编码器工厂
    AVEncoder::FVideoEncoderFactory& Factory = AVEncoder::FVideoEncoderFactory::Get();

    // 创建编码器输入对象
    EncoderInput = Factory.CreateInput();

    // 设置编码参数 (FLayerConfig)
    AVEncoder::FLayerConfig Config;
    Config.Width = Width;
    Config.Height = Height;
    Config.MaxFramerate = Framerate;
    // ... 其他参数如码率等

    // 从工厂获取一个可用的 H264 编码器 (插件提供的硬件编码器会被自动选中)
    ActiveEncoder = Factory.CreateEncoder(EncoderInput, TEXT("H264"), Config);

    if (ActiveEncoder.IsValid())
    {
        // 初始化编码器
        ActiveEncoder->Setup(EncoderInput.ToSharedRef(), Config);
        return true;
    }

    return false;
}

void UMyVideoEncoderManager::SubmitFrame(const TArray<FColor>& FrameData)
{
    if (!ActiveEncoder.IsValid() || !EncoderInput.IsValid())
    {
        return;
    }

    // 将原始帧数据转换为编码器输入格式
    // (此处省略了具体转换逻辑，可能需要创建 FVideoEncoderInputFrame)
    TSharedPtr<AVEncoder::FVideoEncoderInputFrame> InputFrame = /* ... */;

    // 编码选项，例如请求一个关键帧
    AVEncoder::FEncodeOptions Options;
    Options.bForceKeyFrame = false;

    // 提交编码任务
    ActiveEncoder->Encode(InputFrame, Options);
}

void UMyVideoEncoderManager::StopEncoding()
{
    if (ActiveEncoder.IsValid())
    {
        ActiveEncoder->Shutdown();
        ActiveEncoder.Reset();
    }
    EncoderInput.Reset();
}
```

## 模块依赖

从插件源码和常见模式推断，该插件模块依赖于以下非通用模块：

| 模块 | 用途 |
|---|---|
| `AVEncoder` | 提供视频编码的抽象框架，是此插件集成的目标。 |
| `RHI` | 用于与渲染硬件接口交互，获取 GPU 设备句柄。 |
| `RHICore` | RHI 的核心支持。 |
| `Renderer` | 可能用于访问渲染资源和设备。 |
| `VulkanRHI` (特定于 AMF) | AMF 编码器在 Vulkan 后端下需要此模块支持。 |
| `D3D11RHI`, `D3D12RHI` (特定于 AMF/NVENC) | AMF 和 NVENC 编码器在 DirectX 后端下需要这些模块支持。 |

*注：实际的 Build.cs 依赖列表未在提供信息中完整列出，上表基于插件功能和同类插件模式推断。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 宏，属于日志系统升级。 |
| 2026-03-02 | `c3f81430` | VulkanRHI: Remove extensions that don't need to be manually loaded anymore from plugin startup: | 调整 Vulkan RHI 扩展加载逻辑，移除了不再需要手动加载的扩展。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次代码替换错误后的重试提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了编号为 CL51314860 的更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复委托初始化时序问题，将 `OnPostEngineInit` 改为 `GetOnPostEngineInit()`。 |

### 维护评价

该插件自2021年10月创建以来已有约4年历史。根据近期Git提交记录（截至2026年4月）显示，插件仍在维护中，但近期更新主要集中在**底层基础设施适配**（如日志宏迁移、委托接口调整、RHI扩展加载）和**Bug回滚**，并未包含新的硬件编码器功能或对现有编码器的重大改进。

**综合评价**：
1.  **稳定性**：作为Beta版本，默认禁用（`EnabledByDefault: false`），表明Epic认为其功能或稳定性尚未达到正式发布的标准。
2.  **活跃度**：维护不频繁，更新内容偏向于跟随引擎核心的API变更，而非插件本身的功能迭代。
3.  **推荐度**：如果项目**严格依赖**AMF或NVENC硬件编码器进行Pixel Streaming等特定场景，且愿意承担Beta版本的不稳定风险，可以启用并使用。但对于通用项目，应优先考虑使用引擎内置的、更稳定的软件编码方案或评估硬件编码器插件在当前UE版本下的实际稳定性。
4.  **注意事项**：使用前务必在目标硬件和驱动版本上进行充分测试，硬件编码器的行为受驱动程序影响很大。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HardwareEncoders)
- [官方文档] (无特定文档)
- [测试用例] (未在提供信息中发现)