# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、预设） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-03-24 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是 UE 的**实时数据流传输框架**，用于将外部设备或应用程序产生的动画数据（动作捕捉、面部捕捉、摄像机跟踪、灯光控制等）实时导入引擎。它解决的核心问题是：**如何在不修改游戏逻辑的前提下，将任意来源的实时数据统一接入引擎的动画、变换和属性系统**。

Live Link 采用**角色（Role）+ 主题（Subject）**的架构设计：
- **Subject（主题）**：一个数据源，持续发送帧数据
- **Role（角色）**：定义数据的语义类型（Basic、Transform、Animation 等），决定数据如何被消费
- **Source（源）**：数据的传输协议（UDP、TCP、ARKit、OptiTrack 等），由独立插件提供

本插件（Animation/LiveLink）是 Live Link 的**核心框架**，包含数据定义、UI 面板、Sequencer 集成、组件系统和多用户同步等完整功能。实际的数据源（如 LiveLinkFace、OptiTrack、Vicon 等）由其他插件提供。

## 使用场景

- 你在做虚拟制片（Virtual Production），需要将 OptiTrack/Vicon 的动捕数据实时驱动场景中的角色 → 用 Live Link + 对应 Source 插件
- 你在做面部动画预览，需要将 iPhone 的 ARKit 面部追踪数据实时映射到 MetaHuman → 用 Live Link + LiveLinkFace Source
- 你需要将外部摄像机跟踪系统（如 Stype、Mo-Sys）的数据实时驱动 UE 中的 CineCamera → 用 Live Link + Camera Role
- 你需要在 Sequencer 中录制实时数据并回放编辑 → 用 Live Link + LiveLinkMovieScene 模块
- 你需要在多台机器间同步 Live Link 数据 → 用 LiveLinkMultiUser 模块
- 你需要将 Live Link 数据绑定到 Actor 组件上自动驱动 → 用 LiveLinkComponents 模块

## 蓝图用法

Live Link 核心模块提供大量 BlueprintCallable API，以下按功能分组。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLiveLinkSubjects` | 获取所有可用的 Live Link 主题列表 | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkSubjectRole` | 获取指定主题的角色类型 | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkSubjectFrameData` | 获取指定主题的当前帧数据 | `ULiveLinkBlueprintLibrary` |
| `GetLiveLinkSubjectStaticData` | 获取指定主题的静态数据（骨骼结构等） | `ULiveLinkBlueprintLibrary` |
| `IsLiveLinkSubjectEnabled` | 检查指定主题是否启用 | `ULiveLinkBlueprintLibrary` |
| `SetLiveLinkSubjectEnabled` | 启用/禁用指定主题 | `ULiveLinkBlueprintLibrary` |

### 组件节点（LiveLinkComponents 模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSubjectRepresentation` | 设置组件绑定的 Live Link 主题和角色 | `ULiveLinkComponentController` |
| `GetSubjectRepresentation` | 获取当前绑定的主题和角色 | `ULiveLinkComponentController` |

### Sequencer 录制节点（LiveLinkMovieScene 模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecordFrame` | 向 Sequencer Section 录入一帧 Live Link 数据 | `UMovieSceneLiveLinkSection` |
| `FinalizeSection` | 完成录制，可选优化关键帧 | `UMovieSceneLiveLinkSection` |
| `CreateChannelProxy` | 创建 Sequencer 通道代理 | `UMovieSceneLiveLinkSection` |

### 使用示例（蓝图描述）

**示例 1：获取 Live Link 主题数据**

1. 创建一个 `GetLiveLinkSubjects` 节点，输出主题名称数组
2. 遍历数组，对每个主题调用 `GetLiveLinkSubjectRole` 检查角色类型
3. 如果是 Animation Role，调用 `GetLiveLinkSubjectFrameData` 获取骨骼变换数据
4. 将变换数据应用到 SkeletalMeshComponent

**示例 2：使用 LiveLinkComponentController**

1. 在 Actor 上添加 `LiveLinkComponentController` 组件
2. 在 Details 面板中设置 Subject Name 和 Role
3. 组件会自动将 Live Link 数据驱动到 Actor 的变换或骨骼

## C++ 用法

### 头文件引入

```cpp
// Live Link 核心
#include "LiveLinkTypes.h"
#include "LiveLinkRole.h"
#include "LiveLinkPresetTypes.h"

// Live Link MovieScene（Sequencer 集成）
#include "MovieScene/MovieSceneLiveLinkSection.h"
#include "MovieScene/MovieSceneLiveLinkTrack.h"
#include "MovieScene/MovieSceneLiveLinkSubSection.h"

// Live Link 组件
#include "LiveLinkComponentController.h"
```

### 基本用法：创建 Live Link Sequencer Track

以下代码演示如何以编程方式创建 Live Link Sequencer 轨道并录制数据。

```cpp
// 来源: MovieSceneLiveLinkTrack.h, MovieSceneLiveLinkSection.h

// 1. 创建 Live Link Track
UMovieSceneLiveLinkTrack* LiveLinkTrack = Sequence->AddTrack<UMovieSceneLiveLinkTrack>(MovieScene::GetBindingID(CameraBinding));

// 2. 设置 Track 的角色类型
LiveLinkTrack->SetTrackRole(ULiveLinkBasicRole::StaticClass());

// 3. 创建 Section
UMovieSceneLiveLinkSection* Section = Cast<UMovieSceneLiveLinkSection>(LiveLinkTrack->CreateNewSection());

// 4. 初始化 Section（传入主题预设和静态数据）
FLiveLinkSubjectPreset SubjectPreset;
SubjectPreset.Key.SubjectName = FName("MySubject");
SubjectPreset.Role = ULiveLinkBasicRole::StaticClass();
Section->Initialize(SubjectPreset, StaticDataSharedPtr);

// 5. 录制帧数据
FFrameNumber FrameNumber(0);
Section->RecordFrame(FrameNumber, FrameData);

// 6. 完成录制并优化关键帧
FKeyDataOptimizationParams OptimizationParams;
Section->FinalizeSection(true, OptimizationParams);
```

### 进阶用法：自定义属性处理器

Live Link MovieScene 模块使用 `IMovieSceneLiveLinkPropertyHandler` 接口处理不同类型的属性数据。框架内置了三种处理器：

```cpp
// 来源: IMovieSceneLiveLinkPropertyHandler.h, MovieSceneLiveLinkPropertyHandler.h

// 1. 通用属性处理器（模板类，支持 float/int/bool/byte/string）
// FMovieSceneLiveLinkPropertyHandler<T> 处理标量属性
// 自动创建对应的 MovieScene Channel（FloatChannel, IntegerChannel 等）

// 2. 变换处理器 - 处理 FTransform 数组
// FMovieSceneLiveLinkTransformHandler
// 内部使用 FLiveLinkTransformKeys 缓冲变换数据
// 自动处理欧拉角翻转（Euler Flips）问题

// 3. 枚举处理器 - 处理枚举属性
// FMovieSceneLiveLinkEnumHandler
// 枚举值以 int64 存储，但使用 ByteChannel

// 使用属性绑定工具类读写结构体属性
FLiveLinkStructPropertyBindings Binding(PropertyName, PropertyPath);
Binding.CacheBinding(*ScriptStruct);

// 读取属性值
float Value = Binding.GetCurrentValueAt<float>(0, *ScriptStruct, FrameData);

// 写入属性值
Binding.SetCurrentValueAt<float>(0, *ScriptStruct, OutFrameData, NewValue);
```

### 进阶用法：SubSection 系统

Live Link 使用 SubSection 模式管理不同类型的数据录制：

```cpp
// 来源: MovieSceneLiveLinkSubSection.h, MovieSceneLiveLinkSubSectionBasicRole.h

// SubSection 类型：
// - UMovieSceneLiveLinkSubSectionBasicRole  : 处理 Basic Role 的属性
// - UMovieSceneLiveLinkSubSectionAnimation  : 处理动画/变换数据
// - UMovieSceneLiveLinkSubSectionProperties : 处理自定义可插值属性

// 获取指定角色对应的 SubSection 类型
TArray<TSubclassOf<UMovieSceneLiveLinkSubSection>> SubSectionClasses = 
    UMovieSceneLiveLinkSubSection::GetLiveLinkSubSectionForRole(MyRoleClass);

// 自定义 SubSection：继承 UMovieSceneLiveLinkSubSection 并重写
class UMyCustomSubSection : public UMovieSceneLiveLinkSubSection
{
    virtual void Initialize(TSubclassOf<ULiveLinkRole> InSubjectRole, 
                           const TSharedPtr<FLiveLinkStaticDataStruct>& InStaticData) override;
    virtual int32 CreateChannelProxy(int32 InChannelIndex, TArray<bool>& OutChannelMask, 
                                    FMovieSceneChannelProxyData& OutChannelData) override;
    virtual void RecordFrame(FFrameNumber InFrameNumber, 
                            const FLiveLinkFrameDataStruct& InFrameData) override;
    virtual void FinalizeSection(bool bReduceKeys, 
                                const FKeyDataOptimizationParams& OptimizationParams) override;
    virtual bool IsRoleSupported(const TSubclassOf<ULiveLinkRole>& RoleToSupport) const override;
};
```

## Demo 示例

以下是一个最小的自定义 Live Link Role 示例，展示如何定义自己的 Live Link 数据类型：

```cpp
// MyLiveLinkRole.h
#pragma once

#include "LiveLinkRole.h"
#include "MyLiveLinkRole.generated.h"

// 自定义帧数据结构
USTRUCT(BlueprintType)
struct FMyLiveLinkFrameData : public FLiveLinkBaseFrameData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MyData")
    float CustomFloat;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MyData")
    FVector CustomVector;
};

// 自定义静态数据结构
USTRUCT(BlueprintType)
struct FMyLiveLinkStaticData : public FLiveLinkBaseStaticData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MyData")
    FString Description;
};

// 自定义 Role
UCLASS()
class UMyLiveLinkRole : public ULiveLinkRole
{
    GENERATED_BODY()

public:
    virtual UScriptStruct* GetStaticDataStruct() const override { return FMyLiveLinkStaticData::StaticStruct(); }
    virtual UScriptStruct* GetFrameDataStruct() const override { return FMyLiveLinkFrameData::StaticStruct(); }
    virtual UScriptStruct* GetBlueprintDataStruct() const override { return FMyLiveLinkFrameData::StaticStruct(); }
    virtual TSubclassOf<ULiveLinkRole> GetParentRole() const override { return ULiveLinkBasicRole::StaticClass(); }
};
```

```cpp
// MyLiveLinkSource.h - 自定义数据源
#pragma once

#include "LiveLinkSourceFactory.h"
#include "ILiveLinkClient.h"
#include "MyLiveLinkSource.generated.h"

UCLASS()
class UMyLiveLinkSourceFactory : public ULiveLinkSourceFactory
{
    GENERATED_BODY()

public:
    virtual FText GetSourceDisplayName() const override { return NSLOCTEXT("MyLiveLink", "SourceName", "My Custom Source"); }
    virtual FText GetSourceTooltip() const override { return NSLOCTEXT("MyLiveLink", "SourceTooltip", "Custom data source"); }
    virtual EMenuType GetMenuType() const override { return EMenuType::SubPanel; }
    virtual TSharedPtr<SWidget> BuildCreationPanel(FOnLiveLinkSourceCreated OnLiveLinkSourceCreated) const override;
    virtual TSharedPtr<ILiveLinkSource> CreateSource(const FString& ConnectionString) const override;
};
```

## 模块依赖

Live Link 插件包含 7 个模块，以下列出各模块的**独特依赖**（省略 Core/Engine/Slate 等标准依赖）：

| 模块 | 独特依赖 | 用途 |
|---|---|---|
| `LiveLink` | 无特殊依赖（仅标准 Core/Engine/Slate 等） | 核心框架，定义 Role/Subject/Source 接口 |
| `LiveLinkComponents` | `LiveLink` | 提供 LiveLinkComponentController 等蓝图组件 |
| `LiveLinkEditor` | `LiveLink`, `LiveLinkGraphNode` | 编辑器 UI（Live Link 面板、主题管理） |
| `LiveLinkGraphNode` | `LiveLink` | 蓝图节点图集成 |
| `LiveLinkMovieScene` | `LiveLink`, `MovieScene` | Sequencer 录制/回放集成 |
| `LiveLinkMultiUser` | `LiveLink`, `MultiUserClient` | 多用户编辑中的 Live Link 数据同步 |
| `LiveLinkSequencer` | `LiveLink`, `LiveLinkMovieScene`, `Sequencer` | Sequencer 扩展（录制按钮、UI） |

## 维护状态

### 近期更新

```
- 5e30e5e1a996 LiveLink - Fix crash when copy pasting LiveLink subsection into a different level sequence
- fcd8083c3944 Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- 98a8e0e0df23 Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes
```

- 第一条修复了跨 Level Sequence 复制粘贴 SubSection 时的崩溃问题，属于重要的稳定性修复
- 后两条是构建系统和头文件包含的维护性改动，属于 UE5 版本迁移的常规清理

### 维护评价

Live Link 是 Epic Games **持续活跃维护**的核心动画框架。自 2017 年创建以来，它已经成为虚拟制片、动作捕捉和实时动画工作流的基石。该插件：

- ✅ **活跃维护**：作为 UE 动画系统的核心组件，持续获得更新和修复
- ✅ **架构成熟**：Role/Subject/Source 分层设计清晰，扩展性好
- ✅ **生态丰富**：大量第三方 Source 插件（OptiTrack、Vicon、ARKit 等）
- ⚠️ **默认未启用**：`EnabledByDefault=false`，需要在 Plugins 面板手动启用
- ⚠️ **模块众多**：7 个模块的架构对初学者有一定学习门槛

**推荐使用**：任何需要实时外部数据接入 UE 的项目都应考虑使用 Live Link。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/live-link-in-unreal-engine/)