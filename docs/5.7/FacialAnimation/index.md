# Facial Animation Bulk Importer

> Bulk importer for facial animation curves and audio. Imports facial animation curve tables (from FBX) into sound waves.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | FacialAnimation (Runtime), FacialAnimationEditor (Editor) |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/FacialAnimation) | |

## 用途

这个 plugin 解决的核心问题是：**将面部动画曲线数据与音频文件批量绑定**。

在面部动画工作流中，动画师通常使用 Faceware、Dynamixyz 等工具从表演捕捉中提取面部曲线数据（保存为 FBX），同时录音设备会生成对应的音频文件（WAV）。这个 plugin 提供了一套批量导入工具，能够：

1. 扫描指定目录下的所有 FBX 文件
2. 自动匹配同名的 WAV 音频文件
3. 从 FBX 中提取指定节点的动画曲线
4. 将曲线数据嵌入到 SoundWave 资产内部
5. 生成"Audio"曲线用于同步音频播放的预卷时间（pre-roll）

导入完成后，一个 `UAudioCurveSourceComponent` 可以同时播放音频和驱动面部骨骼动画，实现口型同步和表情驱动。

**注意**：此 plugin 标记为 `IsBetaVersion: true`，属于实验性功能，且需要在 Editor Preferences → Experimental 中启用 `FacialAnimationImporter` 选项才会注册导入器面板。

## 使用场景

- 你在做一个需要面部动画同步的角色 → 使用此工具将 FBX 面部曲线 + WAV 音频批量导入为 SoundWave 资产
- 你有一大批从动捕设备导出的面部数据需要处理 → 批量导入器会递归扫描目录并自动配对
- 你需要在 Persona 编辑器中实时预览面部动画与音频的同步效果 → 插件会在 Persona 预览场景中自动创建 `UAudioCurveSourceComponent`

## 蓝图用法

此 plugin 主要面向编辑器工作流，提供的蓝图可用 API 较少。核心的运行时组件 `UAudioCurveSourceComponent` 可在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CurveSourceBindingName` | 曲线源绑定名称，用于在 AnimGraph 中匹配曲线源 | `UAudioCurveSourceComponent` |
| `CurveSyncOffset` | 音频播放位置的时间偏移量，用于调整曲线与音频的同步 | `UAudioCurveSourceComponent` |
| `Play` | 播放音频并同步驱动面部曲线 | `UAudioCurveSourceComponent` |
| `Stop` | 停止播放 | `UAudioCurveSourceComponent` |
| `FadeIn` | 带淡入效果的播放 | `UAudioCurveSourceComponent` |
| `FadeOut` | 带淡出效果的停止 | `UAudioCurveSourceComponent` |

### 使用示例（蓝图描述）

1. 在角色蓝图中添加 `AudioCurveSourceComponent`
2. 设置 `CurveSourceBindingName`（默认为 "Default"）
3. 设置组件的 `Sound` 属性为导入的 SoundWave 资产
4. 在 AnimGraph 中使用 `CurveSourceInterface` 节点连接曲线到 MorphTarget 或骨骼
5. 调用 `Play` 节点开始播放音频并同步驱动面部动画

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块 - 音频曲线源组件
#include "AudioCurveSourceComponent.h"

// Editor 模块 - 批量导入（仅编辑器使用）
#include "FacialAnimationImportItem.h"
#include "FacialAnimationBulkImporterSettings.h"
```

### 基本用法：创建 AudioCurveSourceComponent

```cpp
// 在 Actor 上创建组件（来源：FacialAnimationEditorModule.cpp:20-33）
UAudioCurveSourceComponent* AudioCurveSourceComponent = NewObject<UAudioCurveSourceComponent>(Actor);
AudioCurveSourceComponent->bAlwaysPlay = true;
AudioCurveSourceComponent->CurveSourceBindingName = ICurveSourceInterface::DefaultBinding;

// 设置音频资源
AudioCurveSourceComponent->SetSound(MySoundWave);
AudioCurveSourceComponent->RegisterComponent();
```

### 进阶用法：通过代码导入面部动画

```cpp
// 构造导入项（来源：FacialAnimationImportItem.h）
FFacialAnimationImportItem ImportItem;
ImportItem.FbxFile = TEXT("/path/to/face_animation.fbx");
ImportItem.WaveFile = TEXT("/path/to/voice.wav");
ImportItem.TargetPackageName = TEXT("/Game/Audio/CharacterVoice");
ImportItem.TargetAssetName = TEXT("CharacterVoice_01");

// 执行导入 - 会创建 SoundWave 并嵌入曲线数据
bool bSuccess = ImportItem.Import();
```

### 进阶用法：配置批量导入设置

```cpp
// 获取批量导入设置（来源：FacialAnimationBulkImporterSettings.h）
UFacialAnimationBulkImporterSettings* Settings = GetMutableDefault<UFacialAnimationBulkImporterSettings>();
Settings->SourceImportPath.Path = TEXT("D:/FacialCapture/Character01");
Settings->TargetImportPath.Path = TEXT("/Game/Audio/Character01");
Settings->CurveNodeName = TEXT("blendShapeGroup");
Settings->SaveConfig();
```

## 编辑器用法：批量导入面板

启用此插件后（需在 Editor Preferences → Experimental → 勾选 FacialAnimationImporter），可以通过以下步骤使用批量导入功能：

1. 打开编辑器菜单：**Window → Facial Anim Importer**
2. 在面板中设置 **Source Import Path**：FBX 和 WAV 文件所在的本地目录
3. 设置 **Target Import Path**：UE 项目内容浏览器中的目标路径
4. 设置 **Curve Node Name**：FBX 文件中包含面部曲线的节点名称
5. 点击 **Import All** 按钮

导入器会递归扫描源目录，对于每个 FBX 文件：
- 如果存在同名 WAV 文件 → 将 WAV 导入为 SoundWave，并将 FBX 中的曲线数据嵌入其中
- 如果不存在 WAV 文件 → 当前版本会跳过（仅支持曲线+音频配对导入）

## Demo 示例

### 最小运行时示例

```cpp
// MyFaceAnimActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyFaceAnimActor.generated.h"

class UAudioCurveSourceComponent;

UCLASS()
class AMyFaceAnimActor : public AActor
{
    GENERATED_BODY()

public:
    AMyFaceAnimActor();

    UPROPERTY(VisibleAnywhere)
    UAudioCurveSourceComponent* FaceAudioComponent;

    UFUNCTION(BlueprintCallable)
    void PlayFaceAnimation();
};

// MyFaceAnimActor.cpp
#include "MyFaceAnimActor.h"
#include "AudioCurveSourceComponent.h"

AMyFaceAnimActor::AMyFaceAnimActor()
{
    FaceAudioComponent = CreateDefaultSubobject<UAudioCurveSourceComponent>(TEXT("FaceAudio"));
    FaceAudioComponent->CurveSourceBindingName = FName("FaceCurves");
    FaceAudioComponent->CurveSyncOffset = 0.0f;
    RootComponent = FaceAudioComponent;
}

void AMyFaceAnimActor::PlayFaceAnimation()
{
    FaceAudioComponent->Play();
}
```

**Build.cs 依赖**：

```csharp
// 运行时使用 AudioCurveSourceComponent
PublicDependencyModuleNames.AddRange(new string[] { "FacialAnimation" });

// 仅编辑器批量导入功能（不需要手动依赖，通过编辑器模块自动加载）
```

## 模块依赖

### FacialAnimation（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `InputCore` | 输入核心 |
| `Engine` | 引擎核心功能 |
| `AudioExtensions` | 音频扩展接口 |
| `AudioMixer` | 音频混音器 |

### FacialAnimationEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `FacialAnimation` | 运行时模块依赖 |
| `SlateCore` / `Slate` | UI 框架 |
| `UnrealEd` | 编辑器核心 |
| `AudioEditor` | 音频资产编辑器 |
| `Persona` | 骨骼动画编辑器（预览场景集成） |
| `PropertyEditor` | 属性面板 |
| `DesktopPlatform` | 文件系统对话框 |
| `WorkspaceMenuStructure` | 工作区菜单注册 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 工具链改进，自动添加内联生成代码宏，无功能变化 |
| 2025-04-23 | `6ae5733` | Used UnrealGame build target to convert files to dllstorage | DLL 导出符号规范化，编译系统维护 |
| 2023-01-16 | `bbc37aa` | Another batch iwyu updates to reduce includes | IWYU（Include What You Use）头文件清理，无功能变化 |

### 维护评价

- **年龄**：创建于 2016 年 11 月，已超过 9 年
- **活跃度**：最近 3 次更新均为编译系统/工具链维护，**没有任何功能性更新**
- **实验性状态**：`.uplugin` 中 `IsBetaVersion: true`，需要手动在实验性设置中启用
- **代码成熟度**：代码非常精简（运行时仅 1 个组件类，编辑器仅批量导入器），功能稳定
- **已知限制**：
  - 仅支持 SoundWave 类型的音频资源（不支持 Sound Cue 等随机化类型）
  - 批量导入器仅支持 FBX + WAV 配对模式
  - `UFacialAnimationBulkImporterSettings` 标记为 `Experimental`
  - `UAudioCurveSourceComponent` 标记为 `Experimental`
- **综合评价**：这是一个**长期未有实质性更新的实验性功能**。代码自 2016 年以来功能基本没有变化，最近的提交都是构建系统的批量维护操作。如果你的项目有简单的面部动画音频同步需求可以使用，但对于复杂需求建议考虑 MetaHuman Animator 或 Live Link Face 等更现代的方案。

⚠️ **警告**：此 plugin 超过 2 年没有功能性更新，且始终处于实验（Beta）状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/FacialAnimation)
- 官方文档：无（DocsURL 为空）
- 测试用例：无（Engine/Tests 下未找到相关测试文件）
