# TechAudioTools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 插件并非一个通用的音频播放或混音工具，而是一套专注于**音频参数数据转换与UI/编辑器集成**的底层工具库。它解决的核心问题是：音频系统内部使用的数值（如线性增益、频率倍数）与用户界面（UI控件、编辑器旋钮）中期望显示和编辑的数值（如分贝、半音）之间的转换与映射。此外，它利用MVVM模式简化了音频组件状态（播放、停止、淡入淡出等）与UI控件的绑定过程，使得开发者能够快速创建数据驱动的音频控制界面。

## 使用场景

-   你正在使用MetaSound或其他自定义音频图，需要为其参数创建编辑器工具或自定义UI控件，希望控件显示的单位（如dB、Hz）与音频图内部使用的单位（如线性值、倍数）不同且能自动转换。
-   你需要开发一个自定义的音频预设编辑器或工具，需要统一处理音频参数的范围映射和单位转换逻辑。
-   你希望使用MVVM模式将音频组件（UAudioComponent）的播放状态同步到UI，而不想手动编写大量的事件绑定代码。

## 蓝图用法

### 核心节点

#### 参数映射 (`UTechAudioToolsFloatMapping`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Source To Display` | 将内部系统使用的源数值转换为UI显示的数值。 | `UTechAudioToolsFloatMapping` |
| `Display To Source` | 将UI显示的数值转换为内部系统使用的源数值。 | `UTechAudioToolsFloatMapping` |
| `Normalized To Source` | 将归一化（0-1）数值转换为源范围对应的值。 | `UTechAudioToolsFloatMapping` |
| `Source To Normalized` | 将源数值归一化到0-1范围内。 | `UTechAudioToolsFloatMapping` |
| `Normalized To Display` | 将归一化（0-1）数值转换为显示范围对应的值。 | `UTechAudioToolsFloatMapping` |
| `Display To Normalized` | 将显示数值归一化到0-1范围内。 | `UTechAudioToolsFloatMapping` |
| `Get Source Min` | 获取源范围的最小值。 | `UTechAudioToolsFloatMapping` |
| `Get Source Max` | 获取源范围的最大值。 | `UTechAudioToolsFloatMapping` |
| `Get Display Min` | 获取显示范围的最小值。 | `UTechAudioToolsFloatMapping` |
| `Get Display Max` | 获取显示范围的最大值。 | `UTechAudioToolsFloatMapping` |
| `Get Units` | 获取源端点或显示端点使用的单位。 | `UTechAudioToolsFloatMapping` |

#### 音频组件视图模型 (`UAudioComponentViewModel`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Audio Component` | 将视图模型绑定到一个`UAudioComponent`实例，开始监听其状态变化。 | `UAudioComponentViewModel` |
| `Get Play State` | 获取音频组件的播放状态（播放中、停止、淡入等）。 | `UAudioComponentViewModel` |
| `Is Playing` | 判断音频组件是否正在播放。 | `UAudioComponentViewModel` |
| `Is Stopped` | 判断音频组件是否已停止。 | `UAudioComponentViewModel` |
| `Is Fading In` | 判断音频组件是否正在淡入。 | `UAudioComponentViewModel` |
| `Is Fading Out` | 判断音频组件是否正在淡出。 | `UAudioComponentViewModel` |
| `Is Virtualized` | 判断音频组件是否已被虚拟化（如被距离剔除）。 | `UAudioComponentViewModel` |

### 使用示例（蓝图描述）

1.  **创建一个将频率倍数映射到半音显示的控件**：
    1.  在蓝图中创建 `UTechAudioToolsFloatMapping` 类的变量。
    2.  在细节面板中，将 `Mapping Type` 设置为 `Pitch`。
    3.  将 `Source Pitch Units` 设置为 `Frequency Multiplier`，将 `Display Pitch Units` 设置为 `Semitones`。
    4.  为你的UI滑块（Slider）控件添加一个事件。在事件中，将滑块的 `Value` 作为 `Display` 输入连接到 `Display To Source` 节点，得到 `Source` 值。
    5.  将 `Source` 值设置到你的MetaSound参数或音频组件上。
    6.  反之，将音频参数的值作为 `Source` 输入连接到 `Source To Display` 节点，用返回的 `Display` 值去更新滑块控件的位置，即可实现双向同步。

2.  **监控音频组件状态**：
    1.  创建一个 `UAudioComponentViewModel` 的变量。
    2.  在音频组件开始播放时（如 `Event BeginPlay`），调用 `Set Audio Component` 并传入该音频组件。
    3.  该ViewModel的属性（如 `Is Playing`, `Play State`）会通过FieldNotify机制自动更新。
    4.  在UMG控件中，可以通过 `Property Binding` 将 `TextBlock` 的文本直接绑定到 `Get Play State` 函数，并选择格式化输出状态名称。

## C++ 用法

### 头文件引入

```cpp
#include "TechAudioToolsFloatMapping.h"
#include "AudioComponentViewModel.h"
```

### 基本用法

创建一个用于将线性增益（0.0-1.0）映射到分贝显示（-60dB 到 6dB）的映射器，并进行转换。

```cpp
// 创建一个映射器对象实例
UTechAudioToolsFloatMapping* VolumeMapper = NewObject<UTechAudioToolsFloatMapping>();
// 配置为Volume映射模式
VolumeMapper->MappingType = ETechAudioToolsFloatMappingType::Volume;
VolumeMapper->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
VolumeMapper->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;
VolumeMapper->DisplayRange_Decibels = FFloatInterval(-60.f, 6.f);

// 将内部系统使用的线性增益值转换为UI显示的分贝值
float InternalLinearGain = 0.25f;
float DisplayDecibels = VolumeMapper->SourceToDisplay(InternalLinearGain);
// DisplayDecibels ≈ -12.04 dB

// 将UI中设置的分贝值转换回内部系统需要的线性增益
float NewDisplayDecibels = -6.0f;
float NewInternalLinearGain = VolumeMapper->DisplayToSource(NewDisplayDecibels);
// NewInternalLinearGain ≈ 0.5f
```

*来源文件：`Source/TechAudioTools/Public/TechAudioToolsFloatMapping.h`*

### 进阶用法

结合 `UAudioComponentViewModel` 监听音频组件的播放结束事件。

```cpp
// 在某个 Actor 或 Widget 中
UPROPERTY()
TObjectPtr<UAudioComponentViewModel> AudioViewModel;

UPROPERTY()
TObjectPtr<UAudioComponent> MyAudioComponent;

void AMyActor::SetupAudioMonitoring()
{
    AudioViewModel = NewObject<UAudioComponentViewModel>(this);
    // 绑定到音频组件
    AudioViewModel->SetAudioComponent(MyAudioComponent);
}

// 你可以重写 ViewModel 的虚函数来响应状态变化，或者直接查询其属性。
// 例如，在一个每帧更新中：
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (AudioViewModel && AudioViewModel->IsPlaying())
    {
        // 做一些在播放时才需要的逻辑
    }
}
```

*来源文件：`Source/TechAudioTools/Public/Viewmodels/AudioComponentViewModel.h`*

## Demo 示例

一个最小的C++示例，演示如何创建一个音频参数映射器并将其用于一个简单的音频工具逻辑。

```cpp
// MyAudioParameterProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TechAudioToolsFloatMapping.h"
#include "MyAudioParameterProcessor.generated.h"

UCLASS()
class MYPROJECT_API AMyAudioParameterProcessor : public AActor
{
    GENERATED_BODY()

public:
    AMyAudioParameterProcessor();

    // 一个供蓝图或编辑器编辑的、面向用户的音量值（单位：分贝）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
    float UserVolumeDB = 0.f;

    // 获取转换后的、可供音频系统直接使用的线性增益值
    UFUNCTION(BlueprintPure, Category = "Audio")
    float GetInternalLinearGain() const;

    // 设置内部线性增益，并自动更新 UserVolumeDB
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void SetInternalLinearGain(float InLinearGain);

protected:
    virtual void BeginPlay() override;

private:
    // 音量映射器，负责分贝与线性增益的转换
    UPROPERTY(Instanced, EditAnywhere, Category = "Audio")
    TObjectPtr<UTechAudioToolsFloatMapping> VolumeMapping;
};

// MyAudioParameterProcessor.cpp
#include "MyAudioParameterProcessor.h"

AMyAudioParameterProcessor::AMyAudioParameterProcessor()
{
    // 默认创建一个配置好的Volume映射器
    VolumeMapping = NewObject<UTechAudioToolsFloatMapping>(this, TEXT("VolumeMapping"));
    VolumeMapping->MappingType = ETechAudioToolsFloatMappingType::Volume;
    VolumeMapping->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
    VolumeMapping->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;
    VolumeMapping->DisplayRange_Decibels = FFloatInterval(-60.f, 6.f);
}

void AMyAudioParameterProcessor::BeginPlay()
{
    Super::BeginPlay();
    // 初始同步：根据编辑器中设置的 UserVolumeDB 更新内部值
    SetInternalLinearGain(UserVolumeDB);
}

float AMyAudioParameterProcessor::GetInternalLinearGain() const
{
    if (VolumeMapping)
    {
        // 将用户设置的分贝值转换为内部线性增益
        return VolumeMapping->DisplayToSource(UserVolumeDB);
    }
    return 1.f; // 默认单位增益
}

void AMyAudioParameterProcessor::SetInternalLinearGain(float InLinearGain)
{
    if (VolumeMapping)
    {
        // 将内部线性增益转换回分贝值，并更新用户显示的变量
        UserVolumeDB = VolumeMapping->SourceToDisplay(InLinearGain);
    }
}
```

## 模块依赖

该插件本身的运行时模块主要依赖于标准引擎模块，其独特依赖体现在其**插件级别**的依赖关系上。

| 模块 | 用途 |
|---|---|
| `Metasound` | 核心音频图系统，本插件的MetaSound扩展和集成依赖于此。 |
| `ModelViewViewModel` | 提供MVVM框架，用于实现`UAudioComponentViewModel`等视图模型类。 |

使用者需要在自己的模块`.Build.cs`中添加对`TechAudioTools`和`TechAudioToolsMetaSound`（如果使用MetaSound相关功能）的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 重构MetaSound引脚类型注册逻辑，并统一了相关编辑器行为。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回滚了一个导致编译错误的改动。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 与前一次提交内容相同的更改，可能是修复后重新提交。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为MetaSound字面量视图模型添加了事务支持，允许撤销/重做操作。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将DocumentConfiguration重命名为MetaSound模板，属于代码重命名/清理。 |

### 维护评价

TechAudioTools是一个非常**年轻**（创建于2025年）且标记为**实验性/Beta**的插件。从最近的提交记录看（截至2026年4月），它正处于**活跃开发**状态，近期的更新集中在MetaSound编辑器集成的改进和代码重构上。

**推荐使用建议**：
- ✅ **推荐用于实验和原型开发**：如果你需要快速构建音频参数的UI或集成MetaSound，这是一个有价值的基础工具库。
- ⚠️ **谨慎用于生产环境**：作为实验性插件，其API和功能可能会在未来版本中发生重大变化。在正式项目中使用前，建议评估锁定特定引擎版本的可能性，或做好跟随API更新的准备。
- 已知问题/限制：目前提供的API相对基础，主要集中于数值转换。更复杂的音频工具逻辑仍需自行实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- 官方文档：无
- 测试用例：暂无在插件目录内发现独立的测试模块或文件。