# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman 配置资产、蓝图资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-22 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 数字人动画制作完整工具链，用于将真实表演（视频/音频）转换为高保真的 MetaHuman 面部动画。

该插件解决了从**表演捕捉到最终动画输出**的全链路问题：
- **面部追踪**（MetaHumanFaceContourTracker）：从视频素材中追踪面部关键点和轮廓
- **面部拟合**（MetaHumanFaceFittingSolver）：将追踪结果拟合到 MetaHuman 骨骼控制系统
- **动画求解**（MetaHumanFaceAnimationSolver）：将拟合数据转换为面部动画曲线
- **身份管理**（MetaHumanIdentity）：管理 MetaHuman 角色的身份和参考数据
- **深度生成**（MetaHumanDepthGenerator）：从单目视频生成深度信息，提升追踪精度
- **语音驱动**（MetaHumanSpeech2Face）：从音频自动生成面部动画（Lip Sync）
- **批量处理**（MetaHumanBatchProcessor）：批量处理多段表演数据
- **管线编排**（MetaHumanPipeline）：将各处理步骤串联为可复用的处理管线
- **Sequencer 集成**（MetaHumanSequencer）：将生成的动画导入 Sequencer 时间线
- **配置管理**（MetaHumanConfig/ConfigEditor）：管理求解器和追踪器的配置参数

## 使用场景

- 你有一段演员面部表演的视频素材 → 使用 CaptureSource + FaceContourTracker 追踪面部，再通过 FaceFittingSolver 和 FaceAnimationSolver 生成动画
- 你只有音频文件需要驱动数字人说话 → 使用 Speech2Face 模块从音频生成口型动画
- 你需要对大量表演数据进行批处理 → 使用 BatchProcessor 模块
- 你需要在 Sequencer 中编辑和组合面部动画 → 使用 MetaHumanSequencer 模块
- 你需要配置面部追踪/拟合的参数 → 使用 MetaHumanConfig + ConfigEditor 模块

## 蓝图用法

MetaHuman Animator 主要是编辑器工具链，大部分功能通过编辑器 UI（工具面板、Asset Actions）操作，而非运行时蓝图节点。核心工作流通过 **MetaHuman Toolkit** 面板和 **MetaHuman Identity** 资产驱动。

### 核心资产类型

| 资产类型 | 说明 |
|---|---|
| `UMetaHumanIdentity` | MetaHuman 身份资产，包含面部参考数据和追踪结果 |
| `UMetaHumanConfig` | 配置资产，存储追踪器和求解器的参数 |
| `UMetaHumanPerformance` | 表演资产，存储处理后的动画数据 |

### 核心编辑器 UI（MetaHumanConfigEditor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SMetaHumanConfigCombo` | 配置选择下拉框控件，用于在属性面板中选择 MetaHuman 配置资产 | `SMetaHumanConfigCombo` |
| `FMetaHumanConfigCustomization` | MetaHuman 配置资产的 Detail 面板自定义布局 | `FMetaHumanConfigCustomization` |

### 使用示例（编辑器工作流描述）

1. **创建 Identity**：Content Browser 右键 → Animation → MetaHuman Identity，创建身份资产
2. **导入参考素材**：在 Identity 编辑器中导入正面/侧面照片或视频帧
3. **面部追踪**：选择素材 → 点击 "Track Face"，系统自动追踪面部轮廓
4. **面部拟合**：追踪完成后 → 点击 "Fit to MetaHuman"，将轮廓拟合到骨骼
5. **生成动画**：导入新的表演视频 → 通过 Pipeline 端到端处理，输出动画曲线
6. **导入 Sequencer**：将生成的动画通过 MetaHumanSequencer 模块拖入 Sequencer 编辑

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanConfig.h"
#include "MetaHumanPerformance.h"
#include "MetaHumanPipeline.h"
```

### MetaHumanConfigEditor — 资产工厂

MetaHumanConfigFactory 实现了自定义资产工厂，用于导入 `.mhaconfig` 格式的配置文件：

```cpp
// 来源: Source/MetaHumanConfigEditor/Private/MetaHumanConfigFactory.h

// 检查文件是否可以被此工厂导入
virtual bool FactoryCanImport(const FString& InFilename) override;

// 从文件创建 MetaHumanConfig 资产
virtual UObject* FactoryCreateFile(
    UClass* InClass, UObject* InParent, FName InName,
    EObjectFlags InFlags, const FString& InFilename,
    const TCHAR* InParms, FFeedbackContext* InWarn,
    bool& bOutOperationCanceled
) override;
```

### MetaHumanConfigEditor — 资产定义

```cpp
// 来源: Source/MetaHumanConfigEditor/Private/AssetDefinitions/AssetDefinition_MetaHumanConfig.h

// 自定义资产在 Content Browser 中的显示名称、颜色、分类
virtual FText GetAssetDisplayName() const override;
virtual FLinearColor GetAssetColor() const override;
virtual TSoftClassPtr<UObject> GetAssetClass() const override;
virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
```

### MetaHumanConfigEditor — Detail 面板自定义

```cpp
// 来源: Source/MetaHumanConfigEditor/Private/Customizations/MetaHumanConfigCustomizations.h

// 通过 IDetailCustomization 接口自定义 MetaHumanConfig 资产的属性面板布局
TSharedRef<IDetailCustomization> FMetaHumanConfigCustomization::MakeInstance();
void FMetaHumanConfigCustomization::CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder);
```

## Demo 示例

以下示例展示如何在编辑器模块中注册 MetaHumanConfig 的 Detail 自定义：

```cpp
// MyEditorModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "MetaHumanConfig.h"
#include "PropertyEditorModule.h"

void FMyEditorModule::StartupModule()
{
    // 注册 MetaHumanConfig 资产的 Detail 面板自定义
    // 注意：MetaHumanConfigEditor 模块已内置注册，此处仅为演示
    FPropertyEditorModule& PropertyModule =
        FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

    PropertyModule.RegisterCustomClassLayout(
        UMetaHumanConfig::StaticClass()->GetFName(),
        FOnGetDetailCustomizationInstance::CreateStatic(
            &FMetaHumanConfigCustomization::MakeInstance
        )
    );
}

void FMyEditorModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded("PropertyEditor"))
    {
        FPropertyEditorModule& PropertyModule =
            FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

        PropertyModule.UnregisterCustomClassLayout(
            UMetaHumanConfig::StaticClass()->GetFName()
        );
    }
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

以下为 MetaHuman Animator 各模块之间的**独特依赖**关系（非通用 Core/Engine/Slate 依赖已省略）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库（面部追踪、拟合、求解等底层实现） |
| `MetaHumanCaptureProtocolStack` | 捕获协议栈（与外部设备通信） |
| `MetaHumanCaptureSource` | 捕获数据源管理 |
| `MetaHumanCaptureUtils` | 捕获工具函数集 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器（依赖 MetaHumanImageViewerEditor） |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器组件 |
| `MetaHumanIdentity` | 身份管理核心（依赖 SkeletalMeshUtilitiesCommon, ControlRigDeveloper, MetaHumanCaptureDataEditor, MetaHumanSDKEditor） |
| `MetaHumanFaceContourTracker` | 面部轮廓追踪算法 |
| `MetaHumanFaceFittingSolver` | 面部拟合求解器 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器 |
| `MetaHumanDepthGenerator` | 深度图生成 |
| `MetaHumanSpeech2Face` | 语音驱动面部动画 |
| `MetaHumanPipeline` | 处理管线编排 |
| `MetaHumanSequencer` | Sequencer 集成 |
| `MetaHumanPerformance` | 表演数据管理 |
| `MetaHumanBatchProcessor` | 批量处理 |
| `MetaHumanPlatform` | 平台抽象层 |
| `MetaHumanToolkit` | 编辑器工具面板 |
| `MetaHumanConfig` | 配置管理（依赖 MetaHumanCoreTechLib） |
| `MetaHumanConfigEditor` | 配置编辑器 UI |
| `MetaHumanFootageIngest` | 素材导入 |
| `MeshTrackerInterface` | 网格追踪接口 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格工具 |
| `ControlRigDeveloper` | ControlRig 开发者工具 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护中** ⭐⭐⭐⭐⭐

- 创建于 2023 年（约 3 年），属于较新的官方核心功能插件
- 最近更新非常频繁，5 月 20-22 日连续 3 天有多次功能性提交，涵盖 bug 修复和新功能
- 由 Epic Games 官方维护，是 MetaHuman 生态系统的核心组成部分
- 28 个模块覆盖了从捕获到动画输出的完整链路，工程量庞大但组织清晰
- **强烈推荐使用**：这是 Epic 官方的 MetaHuman 动画制作标准工具，任何涉及 MetaHuman 面部动画的项目都应使用此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档（.uplugin 中未提供）