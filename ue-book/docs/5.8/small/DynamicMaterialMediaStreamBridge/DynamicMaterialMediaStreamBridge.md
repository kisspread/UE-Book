# Material Designer Media Stream Bridge

> Integrates the Media Stream plugin with the Material Designer.

| 属性 | 值 |
|---|---|
| 中文名 | 材质设计器媒体流桥接 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DynamicMaterialMediaStreamBridge` (Runtime), `DynamicMaterialMediaStreamBridgeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge) | |

## 用途

该插件是 **DynamicMaterial（材质设计器）** 和 **MediaStream（媒体流）** 两个系统之间的桥接层。它解决的核心问题是：如何在材质设计器中使用媒体流（如视频、实时视频源）作为材质的纹理输入。

具体来说，插件提供了两个自定义的材质值类型：
- `UDMMaterialValueMediaStream`：静态材质模型的媒体流纹理值
- `UDMMaterialValueMediaStreamDynamic`：动态材质模型的媒体流纹理值

这两个类继承自原有的纹理值类型（`UDMMaterialValueTexture` / `UDMMaterialValueTextureDynamic`），并添加了对 `UMediaStream` 的支持。当媒体流的源或播放器发生变化时，材质会自动更新纹理，实现了媒体流与材质系统的双向联动。

## 使用场景

- 你需要在运行时将视频流（如摄像头画面、网络视频）作为材质纹理显示在 3D 物体上 → 使用材质设计器中的 MediaStream 值类型
- 你在做一个交互式媒体展示项目，需要通过材质设计器编辑视频材质参数 → 同时依赖 DynamicMaterial 和 MediaStream
- 你需要在材质设计器的可视化界面中直接绑定媒体流，而不是手动编写材质节点 → 使用此桥接插件提供的编辑器集成

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMediaStream` | 获取当前绑定的媒体流对象 | `UDMMaterialValueMediaStream` |
| `GetMediaStream` | 获取动态版本中绑定的媒体流对象 | `UDMMaterialValueMediaStreamDynamic` |

### 使用示例（蓝图描述）

1. **获取媒体流**：在蓝图中持有 `UDMMaterialValueMediaStream` 或 `UDMMaterialValueMediaStreamDynamic` 引用后，调用 `GetMediaStream` 节点即可获取其关联的 `UMediaStream` 对象。

2. **编辑器中设置媒体流**：在材质设计器编辑器界面中，找到对应的 MediaStream 值节点，通过属性面板选择或拖入一个 `UMediaStream` 资源。插件会自动订阅媒体流事件，当源或播放器变化时自动更新材质纹理。

3. **序列化支持**：媒体流的绑定关系支持 JSON 序列化/反序列化（`JsonSerialize` / `JsonDeserialize`），可用于材质预设的保存与加载。

## C++ 用法

### 头文件引入

```cpp
#include "DMMaterialValueMediaStream.h"
#include "DMMaterialValueMediaStreamDynamic.h"
```

### 基本用法

获取媒体流纹理值中绑定的媒体流对象：

```cpp
// 假设已获取到 UDMMaterialValueMediaStream 实例
UDMMaterialValueMediaStream* MediaStreamValue = /* ... */;

// 获取关联的媒体流
UMediaStream* Stream = MediaStreamValue->GetMediaStream();
if (Stream)
{
    // 使用媒体流
    UMediaPlayer* Player = Stream->GetPlayer();
    // ...
}
```

对于动态材质模型，使用对应的动态版本：

```cpp
UDMMaterialValueMediaStreamDynamic* DynamicMediaStreamValue = /* ... */;

UMediaStream* Stream = DynamicMediaStreamValue->GetMediaStream();
```

### 进阶用法

在编辑器扩展中，可以通过 JSON 序列化实现媒体流材质值的持久化：

```cpp
// 序列化
TSharedPtr<FJsonValue> JsonValue = MediaStreamValue->JsonSerialize();

// 反序列化
MediaStreamValue->JsonDeserialize(JsonValue);
```

监听媒体流事件（编辑器内部实现，仅供参考）：

```cpp
// 插件内部通过 OnSourceChanged 和 OnPlayerChanged 回调
// 自动将媒体流的纹理输出绑定到材质参数
UFUNCTION()
void OnSourceChanged(UMediaStream* InMediaStream);

UFUNCTION()
void OnPlayerChanged(UMediaStream* InMediaStream);
```

## Demo 示例

```cpp
// MyMediaStreamMaterial.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMMaterialValueMediaStream.h"
#include "MyMediaStreamMaterial.generated.h"

UCLASS()
class AMyMediaStreamMaterial : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaStreamMaterial();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    TObjectPtr<UMediaStream> VideoStream;

    UPROPERTY(BlueprintReadOnly, Category = "Media")
    TObjectPtr<UDMMaterialValueMediaStream> MediaStreamValue;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void ApplyMediaStreamToMaterial();

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyMediaStreamMaterial.cpp
#include "MyMediaStreamMaterial.h"
#include "Materials/DynamicMaterialModel.h"
#include "MediaStream.h"

AMyMediaStreamMaterial::AMyMediaStreamMaterial()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMediaStreamMaterial::BeginPlay()
{
    Super::BeginPlay();
    ApplyMediaStreamToMaterial();
}

void AMyMediaStreamMaterial::ApplyMediaStreamToMaterial()
{
    if (!MediaStreamValue)
    {
        return;
    }

    // 获取绑定的媒体流
    UMediaStream* CurrentStream = MediaStreamValue->GetMediaStream();
    if (CurrentStream)
    {
        UE_LOG(LogTemp, Log, TEXT("Media stream bound: %s"), *CurrentStream->GetName());
    }
}
```

## 模块依赖

从 Build.cs 和 .uplugin 的 Plugins 依赖推断：

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 材质设计器核心插件，提供材质值、材质模型等基础类 |
| `MediaStream` | 媒体流插件，提供 `UMediaStream` 及媒体播放能力 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `82b74724` | [MediaStream] Adding a cache setting override (like MediaPlate does) for using a local cache when us | 为媒体流添加本地缓存设置覆盖，类似 MediaPlate 的实现 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 FSharedString |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退之前的提交 CL51209244 |
| 2026-02-25 | `af0dfacf` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存 |

### 维护评价

- **年龄**：约 1 年，2025 年 1 月创建，属于较新的插件
- **实验性状态**：`IsExperimentalVersion=true`，仍处于实验阶段
- **活跃度**：最近一次更新在 2026 年 5 月，保持活跃维护
- **更新内容**：近期更新主要是基础设施优化（JSON 序列化重构、缓存设置），而非功能新增
- **依赖风险**：同时依赖 DynamicMaterial 和 MediaStream 两个实验性插件，存在级联不稳定性风险
- **推荐程度**：⚠️ **谨慎使用**。作为实验性插件，API 可能发生变化。适合在原型开发阶段探索使用，不建议用于生产环境。建议持续关注 Epic 的更新公告。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge)
- 官方文档（暂无）