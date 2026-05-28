# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、工具、编辑器） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-13 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个功能完整的工具集，用于将真实人类的面部表情和动作捕捉数据驱动到 UE5 的 MetaHuman 虚拟角色上。它解决的核心问题是：如何将 iPhone 或其他设备拍摄的面部视频，经过一系列自动化处理流程（追踪、求解、映射），最终转化为高质量、可用于实时渲染的面部动画序列。

该插件提供了一整套从数据导入、面部特征追踪、表情求解、动画控制映射到最终动画序列导出的完整管线。它不仅仅是简单的面部捕捉，而是包含了面部轮廓追踪、深度图生成、面部动画求解器、面部拟合求解器等复杂的计算机视觉和机器学习算法模块，确保动画的准确性和自然度。

## 使用场景

- **影视级面部动画**：你在制作一个需要高度逼真面部表演的电影或游戏过场动画，使用 iPhone 的“虚实相通”功能拍摄演员的面部表演，然后通过此插件将数据应用到 MetaHuman 角色上，获得高质量的动画。
- **实时虚拟人驱动**：你需要在虚拟直播或实时演示中，通过摄像头驱动 MetaHuman 虚拟形象进行实时口型和表情同步。
- **游戏开发中的面部动画**：你在开发一个叙事驱动的游戏，需要批量处理大量预先录制好的面部表演数据，并将其转化为游戏内角色的动画序列。
- **自定义动画管线**：你需要自定义面部动画的求解参数或映射规则，插件提供的各种解算器和编辑器设置允许进行深度调优。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get MetaHuman Asset Category Path` | 获取在内容浏览器中MetaHuman相关资产的分类路径 | `IMetaHumanCoreEditorModule` |
| `Get MetaHuman Advanced Asset Category Path` | 获取MetaHuman高级资产的分类路径 | `IMetaHumanCoreEditorModule` |

### 编辑器设置（蓝图可读写）

插件提供了一个可配置的编辑器设置类 `UMetaHumanEditorSettings`，其属性暴露为蓝图可读写：

| 属性 | 说明 | 所在类 |
|---|---|---|
| `SampleCount` | A/B对比分割窗口的采样数，影响画质和内存 | `UMetaHumanEditorSettings` |
| `MaximumResolution` | A/B对比分割窗口的最大有效分辨率 | `UMetaHumanEditorSettings` |
| `bForceSerialIngestion` | 是否强制串行化执行导入流程 | `UMetaHumanEditorSettings` |
| `bShowDevelopersContent` | 是否在捕获管理器中显示开发者内容文件夹的源 | `UMetaHumanEditorSettings` |
| `bShowOtherDevelopersContent` | 是否显示其他用户的开发者内容文件夹的源 | `UMetaHumanEditorSettings` |
| `bLoadTrackersOnStartup` | 打开Identity资产时是否自动加载追踪器 | `UMetaHumanEditorSettings` |
| `PerformanceViewSetupSlot1-4` | 用于存储性能编辑器视图配置的插槽 | `UMetaHumanEditorSettings` |

### 使用示例（蓝图描述）

1.  **读取设置**：在蓝图中，使用 `Get Editor Settings` 节点获取 `UMetaHumanEditorSettings` 对象，然后直接读取其属性（如 `SampleCount`）来根据当前设置调整你的蓝图逻辑。
2.  **监听设置变更**：可以绑定到 `UMetaHumanEditorSettings` 的 `OnSettingsChanged` 委托，当用户在编辑器中修改相关设置时，你的蓝图可以收到通知并做出响应。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCoreEditorModule.h"
#include "MetaHumanEditorSettings.h"
```

### 基本用法

**访问编辑器设置**
```cpp
// 获取编辑器设置对象
UMetaHumanEditorSettings* Settings = GetMutableDefault<UMetaHumanEditorSettings>();
if (Settings)
{
    // 读取当前的A/B分割窗口采样数
    int32 CurrentSampleCount = Settings->SampleCount;

    // 修改设置（需要用户有相应权限）
    Settings->SampleCount = 4;
    Settings->PostEditChangeProperty(FPropertyChangedEvent(FindFProperty<UMetaHumanEditorSettings>(GET_MEMBER_NAME_CHECKED(UMetaHumanEditorSettings, SampleCount))));
}
```
*(来源: Public/MetaHumanEditorSettings.h)*

**注册资产分类**
```cpp
// 获取IMetaHumanCoreEditorModule接口
IMetaHumanCoreEditorModule& MetaHumanEditorModule = FModuleManager::LoadModuleChecked<IMetaHumanCoreEditorModule>("MetaHumanCoreEditor");

// 获取插件定义的资产分类路径，用于在内容浏览器中组织资产
TConstArrayView<FAssetCategoryPath> AssetCategories = MetaHumanEditorModule.GetMetaHumanAssetCategoryPath();
TConstArrayView<FAssetCategoryPath> AdvancedAssetCategories = MetaHumanEditorModule.GetMetaHumanAdvancedAssetCategoryPath();

// 在你的资产工厂或编辑器中使用这些分类
```
*(来源: Public/MetaHumanCoreEditorModule.h)*

### 进阶用法

**处理相机标定数据导入**
插件提供了工厂类 `UMetaHumanCameraCalibrationImporterFactory` 用于导入相机标定文件（通常为 `.json` 或特定格式）。
```cpp
// 创建工厂实例
UMetaHumanCameraCalibrationImporterFactory* CalibFactory = NewObject<UMetaHumanCameraCalibrationImporterFactory>();
// 检查一个文件是否可以被导入
bool bCanImport = CalibFactory->FactoryCanImport(TEXT("C:/MyCalibration.json"));
// 如果可以，则调用 FactoryCreateFile 进行导入（通常由编辑器系统触发）
```
*(来源: Public/MetaHumanCameraCalibrationImporterFactory.h)*

## Demo 示例

一个最小化的C++示例，展示如何读取MetaHuman编辑器设置并监听变化。
```cpp
// MyMetaHumanSettingsReader.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "MetaHumanEditorSettings.h"
#include "MyMetaHumanSettingsReader.generated.h"

UCLASS()
class UMyMetaHumanSettingsReader : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    void OnMetaHumanSettingsChanged(const UMetaHumanEditorSettings* ChangedSettings);
};
```
```cpp
// MyMetaHumanSettingsReader.cpp
#include "MyMetaHumanSettingsReader.h"
#include "MetaHumanCoreEditorModule.h"

void UMyMetaHumanSettingsReader::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 订阅设置变更委托
    UMetaHumanEditorSettings* Settings = GetMutableDefault<UMetaHumanEditorSettings>();
    if (Settings)
    {
        Settings->OnSettingsChanged.AddUObject(this, &UMyMetaHumanSettingsReader::OnMetaHumanSettingsChanged);
    }
}

void UMyMetaHumanSettingsReader::Deinitialize()
{
    // 取消订阅
    UMetaHumanEditorSettings* Settings = GetMutableDefault<UMetaHumanEditorSettings>();
    if (Settings)
    {
        Settings->OnSettingsChanged.RemoveAll(this);
    }
    Super::Deinitialize();
}

void UMyMetaHumanSettingsReader::OnMetaHumanSettingsChanged(const UMetaHumanEditorSettings* ChangedSettings)
{
    if (ChangedSettings)
    {
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Settings Changed. New Sample Count: %d"), ChangedSettings->SampleCount);
    }
}
```

## 模块依赖

此插件由大量内部模块组成，模块间存在复杂的依赖关系。对于使用者而言，除了插件本身，通常还需要在项目的 `.Build.cs` 文件中依赖以下外部模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanSDK` | MetaHuman 的基础 SDK，通常包含数据结构和核心功能。 |
| `ControlRig` | 用于将解算出的动画数据应用到 MetaHuman 的骨骼控制器上。 |
| `LiveLinkInterface` | 如果涉及实时面部捕捉（LiveLink），需要此模块接收实时数据流。 |
| `MediaAssets` | 用于处理视频和图像序列的捕获数据源。 |
| `ImageWriteQueue` | 用于异步写入生成的深度图或图像序列。 |
| `MeshDescription` | 用于处理网格数据，特别是在面部拟合过程中。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用了体部追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复MetaHuman角色上的渲染瑕疵问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在进行体部追踪时，过滤掉不必要的可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持将动画序列导出到已有的MetaHuman网格体上。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了Sequencer（序列器）的缓存问题。 |

### 维护评价

- **活跃维护**：该插件在过去一周内有多次实质性更新，修复了渲染、缓存问题，并增加了新功能（如体部追踪兼容性、动画导出灵活性）。
- **核心地位**：作为MetaHuman官方工具链的核心组件，它由Epic Games团队持续维护，与UE5新功能和MetaHuman SDK保持同步。
- **复杂性高**：由于模块众多且涉及复杂的计算机视觉算法，其内部可能存在一定的学习曲线和集成复杂度。
- **推荐使用**：对于任何需要将真实人类表演驱动到MetaHuman虚拟形象的工作流程，此插件是**必备且推荐**的官方解决方案。其活跃的维护状态保证了与最新引擎版本的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档（未提供URL）
- 测试用例（内部测试，路径未明确提供）