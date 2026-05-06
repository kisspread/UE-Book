# Material Designer Media Stream Bridge

> Integrates the Media Stream plugin with the Material Designer.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体流材质桥 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DynamicMaterialMediaStreamBridge` (Runtime), `DynamicMaterialMediaStreamBridgeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge) | |

## 用途

该插件将 **Media Stream** 插件（处理媒体源的流式播放）与 **Material Designer**（动态材质编辑系统）桥接起来。它提供了一个材质值类型 `UDMMaterialValueMediaStream`，允许用户在 Material Designer 中直接使用媒体流作为纹理源，并实时响应媒体源的更改（例如切换视频源、播放器变化），同时支持蓝图访问和控制。

对于需要在动态材质中播放视频、摄像头流或网络流，并且希望利用 Material Designer 的实时编辑与参数化能力的用户，该插件解决了材质与媒体流之间的集成问题。

## 使用场景

- 在 Material Designer 中创建一个使用实时视频流（例如来自摄像头、RTSP 流或文件）作为纹理的材质。
- 在运行时通过蓝图切换媒体源，材质会自动更新纹理。
- 将媒体流作为材质参数，用于动态材质实例（UDMMaterialValueMediaStreamDynamic），支持序列化和属性编辑。
- 结合 Media Stream 插件的远程控制功能，在 Material Designer 内选择媒体源。

## 蓝图用法

该插件公开了少量蓝图可调用节点，主要用于获取媒体流对象。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Media Stream` | 获取当前材质值关联的 `UMediaStream` 对象 | `UDMMaterialValueMediaStream` |
| `Get Media Stream` | 获取动态材质实例关联的 `UMediaStream` 对象 | `UDMMaterialValueMediaStreamDynamic` |

### 使用示例（蓝图描述）

1. **在 Material Designer 中引用媒体流**：在 Material Designer 中创建材质时，添加一个 `MediaStream` 类型的参数（对应 `UDMMaterialValueMediaStream`）。无需额外蓝图节点，材质值会自动连接到指定的 Media Stream 源。

2. **在运行时获取媒体流并操作**：
   - 通过 `Get Media Stream` 节点获取 `UMediaStream` 对象。
   - 使用 Media Stream 插件提供的蓝图节点（如 `Open Source`、`Play`、`Close`）控制媒体播放。
   - 媒体源或播放器发生变更时，材质纹理自动更新（内部通过事件订阅实现）。

## C++ 用法

### 头文件引入

```cpp
#include "DMMaterialValueMediaStream.h"
#include "DMMaterialValueMediaStreamDynamic.h"
```

### 基本用法

**创建媒体流材质值并获取其媒体流（编辑器/运行时）**：

```cpp
// 假设你已经有一个 UDMMaterialValueMediaStream* 实例（例如从材质组件中获取）
UDMMaterialValueMediaStream* MediaStreamValue = ...;
UMediaStream* MediaStream = MediaStreamValue->GetMediaStream();
if (MediaStream)
{
    // 例如：设置媒体源（使用 Media Stream API）
    IMediaStreamPlayer* Player = ...;
    MediaStream->SetMediaSource(Source);
}
```

**在动态材质实例中获取媒体流**：

```cpp
UDMMaterialValueMediaStreamDynamic* DynamicValue = ...;
UMediaStream* MediaStream = DynamicValue->GetMediaStream();
// 操作 MediaStream...
```

### 进阶用法

**自定义材质值子类并覆盖事件（编辑器）**：

在 `UDMMaterialValueMediaStream` 的子类中，可以重写 `OnSourceChanged` 和 `OnPlayerChanged` 方法以对媒体流变化作出特殊处理：

```cpp
void UMyMediaStreamValue::OnSourceChanged(UMediaStream* InMediaStream)
{
    Super::OnSourceChanged(InMediaStream);
    // 当媒体源变化时更新纹理或其他逻辑
    UpdateTextureFromMediaStream();
}
```

**序列化与复制参数（编辑器）**：

这些值支持 JSON 序列化，用于保存/加载材质布局：

```cpp
// 序列化
TSharedPtr<FJsonValue> Json = MediaStreamValue->JsonSerialize();

// 反序列化
bool bSuccess = MediaStreamValue->JsonDeserialize(Json);
```

## Demo 示例

以下是一个最小 C++ 示例，展示如何在 Actor 中获取并操作媒体流材质值。

### MyActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class UDMMaterialValueMediaStream;
class UMediaStream;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UDMMaterialValueMediaStream* MediaStreamValue;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayMediaStream();

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopMediaStream();

private:
    UMediaStream* GetStream() const;
};
```

### MyActor.cpp

```cpp
#include "MyActor.h"
#include "DMMaterialValueMediaStream.h"
#include "MediaStream.h" // 假设 Media Stream 插件提供此类

void AMyActor::PlayMediaStream()
{
    UMediaStream* Stream = GetStream();
    if (Stream)
    {
        // 假设 SetSource 和 Play 是 Media Stream 的 API
        // Stream->SetSource(Source); 
        // Stream->Play();
    }
}

void AMyActor::StopMediaStream()
{
    UMediaStream* Stream = GetStream();
    if (Stream)
    {
        // Stream->Stop();
    }
}

UMediaStream* AMyActor::GetStream() const
{
    return MediaStreamValue ? MediaStreamValue->GetMediaStream() : nullptr;
}
```

## 模块依赖

要使用该插件，你的模块需在 `Build.cs` 中添加以下依赖（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | Material Designer 核心模块，提供材质值基类 |
| `MediaStream` | 媒体流播放与管理模块，提供 `UMediaStream` 等类型 |

## 维护状态

### 近期更新

- 2025-06-13 `b366e598` 保存包含 Media Stream 材质值实例的关卡时不再崩溃
- 2025-05-09 `9070f107` 选择媒体层时自动将遮罩阶段设为"使用基础遮罩"
- 2025-05-09 `19d6a91f` 媒体流播放器变更（以及源变更）现在会正确传播
- 2025-05-09 `c513bc93` 调整材质阶段源选择和层添加菜单顺序
- 2025-05-06 `967c5dd6` 修复源选择器的远程控制集成

### 维护评价

- **创建时间**: 2025-05-06（不足1年）
- **更新频率**: 初始开发阶段，近2个月有多次功能性更新和修复
- **活跃度**: 积极开发中，最新 commit 为 2025-06-13
- **实验性**: 标记为实验性（`IsExperimentalVersion=true`），API 可能变动，但不影响基本使用
- **推荐**: 适合需要将媒体流集成到 Material Designer 中的项目，但需注意实验性标签带来的潜在稳定性风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge)
- [官方文档](https://docs.unrealengine.com/)（无专门文档，可参考 Media Stream 和 Material Designer 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge/Source)（当前无独立测试目录）