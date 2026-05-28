# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数字人资产） |
| 模块 | `MetaHumanCoreEditor` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanSequencer` (Runtime) 等 28 个模块 |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 数字人创作工具包的核心部分。它提供了一整套工作流程，用于从真实演员的视频素材（如 iPhone 深度摄像头拍摄的视频）中创建逼真的数字人面部动画。这个插件解决的核心问题是：如何高效、准确地将现实世界的表演数据转化为可在 Unreal Engine 中使用的高质量数字人动画资产。它整合了面部追踪、模型拟合、动画求解和序列器集成等多个步骤。

## 使用场景

- **影视与虚拟制片**：你需要将演员的面部表演快速转换为数字替身（MetaHuman）的动画，用于实时预览或最终渲染。
- **游戏开发**：你需要为大量 NPC 创建逼真的对话动画，而不是手K每一帧。
- **数字人应用**：你正在开发虚拟主播或数字客服，需要从摄像头视频实时生成面部动画。

## 蓝图用法

### 核心设置节点

`UMetaHumanEditorSettings` 提供了多个可在编辑器中配置的参数，这些参数会影响动画生成的质量和性能。

| 属性 | 说明 | 所在类 |
|---|---|---|
| `SampleCount` | A/B 分割视窗的采样数。数值越高画质越好，但内存占用越大。 | `UMetaHumanEditorSettings` |
| `MaximumResolution` | A/B 分割视窗的最大有效分辨率。 | `UMetaHumanEditorSettings` |
| `bForceSerialIngestion` | 是否强制数据导入过程串行运行。 | `UMetaHumanEditorSettings` |
| `bShowDevelopersContent` | 是否在捕获管理器中显示开发者内容文件夹中的捕获源。 | `UMetaHumanEditorSettings` |
| `bLoadTrackersOnStartup` | 是否在打开“身份”资产时立即加载追踪器。 | `UMetaHumanEditorSettings` |
| `PerformanceViewSetupSlot1` 到 `Slot4` | 用于存储“性能”编辑器视图配置（如 A/B 模式、显示选项）的槽位。 | `UMetaHumanEditorSettings` |

**使用示例（蓝图描述）**
在编辑器的“项目设置” -> “插件” -> “MetaHuman Animator”类别下，可以找到上述设置。调整 `SampleCount` 和 `MaximumResolution` 可以在性能与预览画质之间取得平衡。启用 `bShowDevelopersContent` 可以让你在 MetaHuman 工具中直接访问项目 `Developers` 文件夹下的测试数据。

### 导入节点

`UMetaHumanCameraCalibrationImporterFactory` 是一个工厂类，用于将外部相机校准数据文件导入到 Unreal Engine 中。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FactoryCanImport` | 检查给定文件路径是否可以被此工厂导入。 | `UMetaHumanCameraCalibrationImporterFactory` |
| `Reimport` | 对已导入的相机校准资产执行重新导入操作。 | `UMetaHumanCameraCalibrationImporterFactory` |

**使用示例（蓝图描述）**
通常此工厂通过编辑器的“导入”按钮自动调用。你也可以在蓝图中通过 `UFactory` 的基类函数（如 `FactoryCreateFile`）来调用它，但这属于高级用法，通常直接使用编辑器的拖拽导入功能即可。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanEditorSettings.h"
#include "MetaHumanCameraCalibrationImporterFactory.h"
#include "MetaHumanCoreEditorModule.h"
```

### 基本用法：访问编辑器设置

获取 `MetaHuman Animator` 的全局编辑器设置单例，并读取或修改其属性。

```cpp
// 获取 MetaHuman 编辑器设置的单例
UMetaHumanEditorSettings* Settings = GetMutableDefault<UMetaHumanEditorSettings>();
if (Settings)
{
    // 调整采样数以平衡画质与内存
    Settings->SampleCount = 4;
    // 保存设置到配置文件
    Settings->PostEditChangeProperty(FPropertyChangedEvent(nullptr));
    Settings->TryUpdateDefaultConfigFile();
}
```
*（来源：基于 `UMetaHumanEditorSettings` 类推断的标准访问模式）*

### 进阶用法：模块接口与资产分类

通过模块接口获取 MetaHuman 相关的自定义资产分类路径，这在创建自定义资产编辑器时很有用。

```cpp
// 获取 MetaHumanCoreEditor 模块接口
IMetaHumanCoreEditorModule& CoreEditorModule = FModuleManager::GetModuleChecked<IMetaHumanCoreEditorModule>(TEXT("MetaHumanCoreEditor"));

// 获取标准的 MetaHuman 资产分类路径
TConstArrayView<FAssetCategoryPath> CategoryPaths = CoreEditorModule.GetMetaHumanAssetCategoryPath();

// 在注册自定义资产类型时使用这些路径
// IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
// AssetTools.RegisterAssetTypeActions(..., CategoryPaths[0], ...);
```
*（来源：基于 `IMetaHumanCoreEditorModule` 接口推断）*

## Demo 示例

一个最小的示例，展示如何在 C++ 中获取 MetaHuman 编辑器设置并监听其变化。

**MetaHumanDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "MetaHumanDemo.generated.h"

class UMetaHumanEditorSettings;

UCLASS()
class UMetaHumanDemoSubsystem : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    // 设置变更回调
    void OnEditorSettingsChanged(const FPropertyChangedEvent& PropertyChangedEvent);

    // 设置对象
    UPROPERTY()
    TObjectPtr<UMetaHumanEditorSettings> CachedSettings;
};
```

**MetaHumanDemo.cpp**
```cpp
#include "MetaHumanDemo.h"
#include "MetaHumanEditorSettings.h"

void UMetaHumanDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 获取默认设置对象（非可变，仅观察）
    CachedSettings = GetDefault<UMetaHumanEditorSettings>();
    if (CachedSettings)
    {
        // 绑定设置变更委托
        CachedSettings->OnSettingsChanged.AddUObject(this, &UMetaHumanDemoSubsystem::OnEditorSettingsChanged);
        UE_LOG(LogTemp, Log, TEXT("MetaHumanDemoSubsystem: 已绑定到编辑器设置变更。"));
    }
}

void UMetaHumanDemoSubsystem::Deinitialize()
{
    if (CachedSettings)
    {
        CachedSettings->OnSettingsChanged.RemoveAll(this);
        CachedSettings = nullptr;
    }
    Super::Deinitialize();
}

void UMetaHumanDemoSubsystem::OnEditorSettingsChanged(const FPropertyChangedEvent& PropertyChangedEvent)
{
    if (PropertyChangedEvent.GetPropertyName() == GET_MEMBER_NAME_CHECKED(UMetaHumanEditorSettings, SampleCount))
    {
        int32 NewSampleCount = CachedSettings->SampleCount;
        UE_LOG(LogTemp, Warning, TEXT("MetaHumanDemoSubsystem: A/B视图采样数已变更为: %d"), NewSampleCount);
        // 在此处可以触发依赖此设置的其他逻辑
    }
}
```

## 模块依赖

本插件的各个模块之间相互依赖，形成了复杂的依赖网络。以下列出了使用者最可能需要直接依赖的模块，以及它们提供的独特功能。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 核心功能，通常作为基础被其他模块依赖。 |
| `MetaHumanCoreEditor` | 编辑器扩展，提供资产分类、编辑器设置等。 |
| `MetaHumanIdentity` | 管理和创建 MetaHuman “身份”资产。 |
| `MetaHumanPerformance` | 管理和播放面部“性能”动画资产。 |
| `MetaHumanPipeline` | 处理数据导入和处理的“管道”系统。 |
| `MetaHumanFaceFittingSolver` | 执行面部模型拟合的核心算法。 |
| `MetaHumanSpeech2Face` | （可选）基于语音生成面部动画。 |
| `MetaHumanSequencer` | 将面部动画集成到 Sequencer 时间线。 |

*注意：此插件依赖大量特定于 MetaHuman 的库（如 `MetaHumanCoreTechLib`）和 UE 编辑器模块，通常无需在游戏项目模块中直接添加依赖，而是通过插件提供的蓝图节点和资产进行工作。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列的导出功能，避免冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时，过滤掉不必要的可视化对象，优化性能。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 新增功能：可将动画序列导出到已有的网格体上。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存相关问题，提升稳定性。 |

### 维护评价

MetaHuman Animator 是 Epic Games 官方维护的旗舰级数字人工具。基于最近的提交历史（2026年5月），该插件正处于**活跃开发**阶段。更新内容涵盖功能增强（如新导出选项）、Bug 修复（渲染、缓存）和性能优化（可视化对象过滤）。

**优点**：作为官方核心工具，有持续的资金和技术投入，功能不断迭代和完善。
**注意点**：插件结构非常庞大，模块众多，对初学者可能有一定学习曲线。部分高级功能可能需要配合 MetaHuman Creator 和其他云服务。

**推荐使用**：如果你正在或计划使用 MetaHuman 数字人进行内容创作，这是必不可少的官方工具链，强烈推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests)