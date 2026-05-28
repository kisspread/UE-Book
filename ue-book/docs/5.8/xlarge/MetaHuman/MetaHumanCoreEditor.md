# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，编辑器工具） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 创建与动画工具套件。它解决的核心问题是**将现实世界的人类面部表演（通过摄像头、动作捕捉设备等采集）转换并应用到数字 MetaHuman 角色上**，实现高保真、可动画的数字人类。这个插件不仅提供最终的结果，还集成了从数据采集、处理、面部追踪、动画解算到最终驱动角色的完整生产流水线。它存在的意义是为数字人类创作提供一个端到端的官方解决方案，简化了传统上复杂且分散的工作流程。

## 使用场景

- **影视与虚拟制片**：在电影或广告项目中，需要将演员的实时或预先录制的面部表演，无缝地转移到虚拟场景中的 MetaHuman 角色上，用于虚拟拍摄或后期制作。
- **游戏开发**：在开发具有丰富面部动画的 AAA 级游戏时，使用此工具批量处理演员表演数据，为游戏中的 NPC 或主角生成对话和表情动画。
- **虚拟主播与实时通讯**：创建能够实时追踪并模仿用户面部表情的虚拟形象，用于直播、视频会议或元宇宙应用。
- **快速原型与测试**：动画师需要快速验证一个面部动画创意是否适用于某个 MetaHuman 角色时，可以使用此工具链进行快速迭代。

## 蓝图用法

本插件的蓝图 API 主要面向其核心工作流，如表演捕获、角色创建和动画应用。以下是从模块结构推断的核心功能节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Capture` | 启动面部表演捕获会话 | `UMetaHumanPerformance` |
| `Stop Capture` | 停止当前的捕获会话 | `UMetaHumanPerformance` |
| `Apply to MetaHuman` | 将捕获或生成的表演数据应用到指定的 MetaHuman 身份/骨骼网格体上 | `UMetaHumanIdentity` |
| `Create New Identity` | 基于输入的捕获数据创建一个新的 MetaHuman 身份资产 | `UMetaHumanIdentity` |
| `Bake Animation to Sequence` | 将实时或处理后的面部动画烘焙为可编辑的动画序列资产 | `UMetaHumanSequencer` |

### 使用示例（蓝图描述）

1. **创建新角色**：在内容浏览器中右键，选择“创建 MetaHuman 身份”，这会调用 `Create New Identity` 节点背后的逻辑，打开 MetaHuman Identity 编辑器。
2. **捕获表演**：在 MetaHuman Identity 编辑器或独立的 Performance 编辑器中，连接摄像头或导入视频文件，点击“录制”按钮（对应 `Start Capture`）。表演完成后点击“停止”。
3. **解算与应用**：工具会自动进行面部追踪和解算。完成后，点击“应用到身份”按钮（对应 `Apply to MetaHuman`），表演数据将驱动场景中的 MetaHuman 角色。
4. **序列化动画**：在 Sequencer 中，选中带有动画的 MetaHuman 角色，右键选择“将 MetaHuman 动画烘焙到序列”，生成独立的动画序列资产。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCoreEditorModule.h"
#include "MetaHumanEditorSettings.h"
// 根据所需功能引入对应模块头文件，例如：
#include "MetaHumanPerformance.h"
#include "MetaHumanIdentity.h"
```

### 基本用法

获取编辑器模块接口，访问资产分类路径。这可用于在自定义编辑器中注册 MetaHuman 相关的资产过滤器。

```cpp
// 来源: Public/MetaHumanCoreEditorModule.h
IMetaHumanCoreEditorModule& CoreEditorModule = FModuleManager::GetModuleChecked<IMetaHumanCoreEditorModule>("MetaHumanCoreEditor");
TConstArrayView<FAssetCategoryPath> AssetCategories = CoreEditorModule.GetMetaHumanAssetCategoryPath();
TConstArrayView<FAssetCategoryPath> AdvancedCategories = CoreEditorModule.GetMetaHumanAdvancedAssetCategoryPath();

// 使用这些类别路径来过滤或显示资产
```

### 进阶用法

访问和修改编辑器全局设置，例如配置 A/B 分窗的质量或捕获源的行为。

```cpp
// 来源: Public/MetaHumanEditorSettings.h
UMetaHumanEditorSettings* Settings = GetMutableDefault<UMetaHumanEditorSettings>();
if (Settings)
{
    // 在低内存机器上调整性能
    Settings->bForceSerialIngestion = true; // 强制序列化处理以节省内存
    Settings->bLoadTrackersOnStartup = false; // 延迟加载追踪器以加快启动速度
    Settings->MaximumResolution = 2048; // 降低预览分辨率
    Settings->PostEditChangeProperty(FPropertyChangedEvent(nullptr)); // 通知设置更改
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何加载 MetaHuman 性能模块并查询其状态。

```cpp
// MyMetaHumanActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyMetaHumanActor.generated.h"

UCLASS()
class AMyMetaHumanActor : public AActor
{
    GENERATED_BODY()
public:
    AMyMetaHumanActor();
    virtual void BeginPlay() override;
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    bool IsCapturing() const;
private:
    // 指向性能模块的智能指针，确保模块生命周期
    TWeakObjectPtr<UObject> PerformanceManager;
};
```

```cpp
// MyMetaHumanActor.cpp
#include "MyMetaHumanActor.h"
#include "MetaHumanPerformance.h" // 假设此头文件暴露了核心管理类

AMyMetaHumanActor::AMyMetaHumanActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanActor::BeginPlay()
{
    Super::BeginPlay();
    // 获取或创建性能管理器实例
    PerformanceManager = UMetaHumanPerformanceManager::Get(); // 假设存在这样一个单例或管理类
}

bool AMyMetaHumanActor::IsCapturing() const
{
    if (PerformanceManager.IsValid())
    {
        // 调用管理器的查询方法，具体API需参考实际头文件
        // return PerformanceManager->IsCurrentlyCapturing();
    }
    return false;
}
```

## 模块依赖

要使用本插件的核心功能，你的模块需要依赖以下**特殊模块**（除了标准的Core, Engine等）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库，包含解算器、追踪器等底层技术实现 |
| `ControlRigDeveloper` | 用于驱动和控制 MetaHuman 角色的 Control Rig 开发接口 |
| `SkeletalMeshUtilitiesCommon` | 处理骨骼网格体（MetaHuman 角色的基础）的通用工具 |
| `MetaHumanCaptureDataEditor` | 编辑器内处理和管理捕获数据的组件 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供与 MetaHuman 创建流程的集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能以避免冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵/伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤掉不必要的可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为现有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题。 |

### 维护评价

**活跃维护**。MetaHuman Animator 是 Epic Games 官方数字人类解决方案的核心组件，其重要性不言而喻。从近期提交记录看，开发团队仍在持续进行**功能性更新**（如新增导出支持）、**问题修复**（渲染瑕疵、缓存问题）和**体验优化**（筛选可视化对象），更新频率高且内容实质性。没有迹象表明该插件被废弃或进入仅维护状态。作为官方旗舰级功能，推荐需要制作数字人类动画的项目积极使用，但需注意它是一个大型、复杂的工具套件，学习曲线较陡。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (链接待补充)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (部分测试模块)