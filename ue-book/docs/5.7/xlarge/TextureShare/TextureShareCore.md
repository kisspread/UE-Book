# Texture Share

> Share textures and data between processes（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、纹理资产） |
| 模块 | `TextureShareCore` (Runtime), `TextureShare` (Runtime), `TextureShareDisplayCluster` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TextureShare) | |

## 用途

TextureShare 是一个用于在**不同进程之间共享纹理和数据**的插件，主要面向虚拟制片（Virtual Production）场景。它解决了以下核心问题：

1. **跨进程纹理共享**：允许多个 UE 进程或外部应用程序（如 Notch、TouchDesigner、Disguise 等）实时共享 GPU 纹理数据，无需通过文件或网络传输
2. **nDisplay 集成**：与 nDisplay 多显示器系统深度集成，支持在分布式渲染环境中同步纹理
3. **帧同步**：提供帧级别的同步机制，确保多个进程在相同的时间点读写共享数据
4. **灵活的数据交换**：除了纹理外，还可以共享任意二进制数据（如控制参数、状态信息等）

底层使用 **Windows 共享内存（Shared Memory）** 和 **D3D11/D3D12 共享句柄** 实现跨进程通信，因此仅支持 Win64 平台。

## 使用场景

- 你在做虚拟制片的 LED 墙渲染 → 用 TextureShare + nDisplay 在多个渲染节点间同步纹理
- 你需要将 UE 的渲染结果实时发送给外部合成软件（如 Notch、TouchDesigner）→ 用 TextureShare 建立共享通道
- 你在做多机位同步渲染 → 用 TextureShare 在多个 UE 实例间共享场景数据
- 你需要在 UE 和外部控制软件之间交换参数数据 → 用 TextureShare 的数据通道功能

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateShare` | 创建一个纹理共享会话 | `UTextureShareBPLibrary` |
| `DeleteShare` | 删除纹理共享会话 | `UTextureShareBPLibrary` |
| `BeginFrame` | 开始一帧的共享操作 | `UTextureShareBPLibrary` |
| `EndFrame` | 结束一帧的共享操作 | `UTextureShareBPLibrary` |
| `SendTexture` | 发送纹理到共享通道 | `UTextureShareBPLibrary` |
| `ReceiveTexture` | 从共享通道接收纹理 | `UTextureShareBPLibrary` |
| `SendData` | 发送自定义数据 | `UTextureShareBPLibrary` |
| `ReceiveData` | 接收自定义数据 | `UTextureShareBPLibrary` |
| `IsConnected` | 检查是否已连接到远程进程 | `UTextureShareBPLibrary` |

### 使用示例（蓝图描述）

**发送纹理到外部进程：**

1. 在 BeginPlay 中，调用 `CreateShare` 节点，传入共享名称（如 "MyShare"）和进程角色（Server/Client）
2. 在 Tick 事件中：
   - 调用 `BeginFrame` 开始新一帧
   - 调用 `SendTexture`，传入要共享的 RenderTarget 和纹理名称
   - 调用 `EndFrame` 结束当前帧
3. 在 EndPlay 中，调用 `DeleteShare` 清理资源

**接收外部进程的纹理：**

1. 同样在 BeginPlay 中创建共享会话
2. 在 Tick 中：
   - 调用 `BeginFrame`
   - 调用 `ReceiveTexture`，传入目标纹理名称，获取接收到的纹理
   - 将接收到的纹理应用到材质或 UI
   - 调用 `EndFrame`

## C++ 用法

### 头文件引入

```cpp
#include "ITextureShareCore.h"
#include "ITextureShareCoreAPI.h"
#include "TextureShareCoreContainers.h"
```

### 基本用法

```cpp
// 来源: TextureShareCore API 使用示例

// 获取 TextureShareCore 模块接口
ITextureShareCore& TextureShareCoreModule = ITextureShareCore::Get();
ITextureShareCoreAPI& API = TextureShareCoreModule.GetTextureShareCoreAPI();

// 创建共享对象
TSharedPtr<ITextureShareCoreObject> ShareObject = API.CreateShareObject(
    TEXT("MyShareProcess"),
    ETextureShareProcessType::Server,
    ETextureShareDevice::D3D11
);

// 开始帧同步
ShareObject->BeginFrame();

// 发送纹理
FTextureShareCoreTextureDesc TextureDesc;
TextureDesc.TextureName = TEXT("SceneColor");
TextureDesc.Format = ETextureShareFormat::BGRA8;
ShareObject->SendTexture(TextureDesc, TextureRHI);

// 结束帧
ShareObject->EndFrame();
```

### 进阶用法

```cpp
// 来源: TextureShareDisplayCluster 集成示例

// 配置共享策略
FTextureShareCorePolicy Policy;
Policy.bEnableFrameSync = true;
Policy.SyncMode = ETextureShareSyncMode::FrameSync;

// 创建带策略的共享对象
TSharedPtr<ITextureShareCoreObject> ShareObject = API.CreateShareObject(
    TEXT("DisplayClusterShare"),
    ETextureShareProcessType::Server,
    ETextureShareDevice::D3D12,
    Policy
);

// 注册回调以处理连接状态变化
ShareObject->OnConnectionChanged.AddLambda(
    [](const TSharedPtr<ITextureShareCoreObject>& Object, bool bIsConnected)
    {
        UE_LOG(LogTextureShare, Log, TEXT("Connection state: %s"), 
            bIsConnected ? TEXT("Connected") : TEXT("Disconnected"));
    }
);

// 发送自定义数据
TArray<uint8> CustomData;
// ... 填充数据 ...
ShareObject->SendData(TEXT("ControlParams"), CustomData);

// 接收自定义数据
TArray<uint8> ReceivedData;
if (ShareObject->ReceiveData(TEXT("ControlParams"), ReceivedData))
{
    // 处理接收到的数据
}
```

## Demo 示例

### TextureShareSender.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ITextureShareCoreAPI.h"
#include "TextureShareSender.generated.h"

UCLASS()
class ATextureShareSender : public AActor
{
    GENERATED_BODY()

public:
    ATextureShareSender();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "TextureShare")
    FString ShareName = TEXT("DemoShare");

    UPROPERTY(EditAnywhere, Category = "TextureShare")
    UTextureRenderTarget2D* SourceRenderTarget;

private:
    TSharedPtr<ITextureShareCoreObject> ShareObject;
};
```

### TextureShareSender.cpp

```cpp
#include "TextureShareSender.h"
#include "ITextureShareCore.h"
#include "Engine/TextureRenderTarget2D.h"

ATextureShareSender::ATextureShareSender()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ATextureShareSender::BeginPlay()
{
    Super::BeginPlay();

    if (!ITextureShareCore::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("TextureShareCore module not available"));
        return;
    }

    ITextureShareCoreAPI& API = ITextureShareCore::Get().GetTextureShareCoreAPI();
    
    ShareObject = API.CreateShareObject(
        *ShareName,
        ETextureShareProcessType::Server,
        ETextureShareDevice::D3D11
    );

    if (ShareObject.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("TextureShare '%s' created"), *ShareName);
    }
}

void ATextureShareSender::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!ShareObject.IsValid() || !SourceRenderTarget)
    {
        return;
    }

    ShareObject->BeginFrame();

    // 发送场景颜色纹理
    FTextureShareCoreTextureDesc TextureDesc;
    TextureDesc.TextureName = TEXT("SceneColor");
    ShareObject->SendTexture(TextureDesc, SourceRenderTarget->GetResource()->TextureRHI);

    ShareObject->EndFrame();
}

void ATextureShareSender::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ShareObject.IsValid())
    {
        ShareObject->Release();
        ShareObject.Reset();
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | 渲染核心功能，RHI 纹理操作 |
| `RHI` | 渲染硬件接口，D3D11/D3D12 共享句柄 |
| `D3D11RHI` | Direct3D 11 渲染硬件接口实现 |
| `D3D12RHI` | Direct3D 12 渲染硬件接口实现 |
| `DisplayCluster` | nDisplay 多显示器系统集成 |
| `TextureShareCore` | 核心共享逻辑和 API |

## 维护状态

### 近期更新

```
- e9b860652741 [TextureShare] [Virtual Production] Added CPU profiler events.
- 681a90e79c31 [VirtualProduction] [nDisplay] [TextureShare] - fixed Automation test errors for mutex objects.
- 82a5e5d9ef8b [TextureShare] [nDisplay] Fixed numerous of the bugs:
```

### 维护评价

- **创建时间**：2020 年 9 月，约 5 年历史
- **维护状态**：活跃维护中，近期有功能增强（CPU profiler）和 bug 修复
- **实验性标记**：IsBetaVersion=true，API 可能在未来版本中发生变化
- **平台限制**：仅支持 Win64，依赖 Windows 共享内存和 D3D
- **依赖关系**：与 nDisplay 深度集成，需要 nDisplay 插件启用
- **推荐程度**：适合虚拟制片场景，但需注意其 Beta 状态和平台限制

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TextureShare)
- [nDisplay 文档](https://docs.unrealengine.com/5.7/en-US/n-display-in-unreal-engine/)