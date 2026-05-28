# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源、工具资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-03-15 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具链，用于将真实人物的面部表演数据（如 iPhone 深度摄像头捕捉、视频录像等）转换为 MetaHuman 角色的面部动画。

核心解决的问题是：**将真实人脸的运动数据高保真地映射到 MetaHuman 数字角色上**。

该插件提供完整的动画制作流程：
1. **捕获**（Capture）：从设备（如 iPhone）或视频文件获取面部表演数据
2. **追踪**（Tracking）：面部轮廓追踪和网格追踪
3. **拟合**（Fitting）：将追踪数据拟合到 MetaHuman 面部骨骼系统
4. **动画求解**（Animation Solving）：生成最终的面部动画
5. **输出**（Export）：导出动画序列到 Sequencer 或其他格式

## 模块架构

该插件采用 Runtime/Editor 模块分离架构，共 28 个模块。按功能可分为以下子系统：

### 核心基础设施
| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 核心基础功能，通用工具类 |
| `MetaHumanCoreEditor` | 编辑器核心功能 |
| `MetaHumanConfig` | 配置管理 |
| `MetaHumanPlatform` | 平台抽象层 |

### 捕获与数据采集
| 模块 | 用途 |
|---|---|
| `MetaHumanCaptureSource` | 捕获数据源管理 |
| `MetaHumanCaptureUtils` | 捕获工具函数 |
| `MetaHumanCaptureProtocolStack` | 捕获通信协议栈 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器 |
| `MetaHumanFootageIngest` | 素材导入处理 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器 |

### 面部追踪与拟合
| 模块 | 用途 |
|---|---|
| `MetaHumanFaceContourTracker` | 面部轮廓追踪算法 |
| `MetaHumanFaceFittingSolver` | 面部拟合求解器 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器 |
| `MetaHumanDepthGenerator` | 深度图生成 |
| `MeshTrackerInterface` | 网格追踪接口 |

### 身份与动画
| 模块 | 用途 |
|---|---|
| `MetaHumanIdentity` | MetaHuman 身份管理 |
| `MetaHumanPerformance` | 表演数据管理 |
| `MetaHumanSpeech2Face` | 语音驱动面部动画 |
| `MetaHumanSequencer` | Sequencer 集成 |
| `MetaHumanBatchProcessor` | 批量处理 |

### 管线与工具
| 模块 | 用途 |
|---|---|
| `MetaHumanPipeline` | 处理管线 |
| `MetaHumanToolkit` | 通用工具集 |
| `MetaHumanControlsConversionTest` | 控制器转换测试 |

## 使用场景

- 你使用 iPhone 的 TrueDepth 摄像头捕获了面部表演 → 使用 MetaHuman Animator 将捕获数据转换为 MetaHuman 动画
- 你有一段真人面部视频素材 → 使用视频追踪功能提取面部运动并应用到 MetaHuman
- 你有一段语音录音 → 使用 Speech2Face 模块生成口型动画
- 你需要批量处理多个 MetaHuman 的动画数据 → 使用 BatchProcessor
- 你需要将动画导入 Sequencer 进行进一步编辑 → 使用 MetaHumanSequencer 模块

## 蓝图用法

由于源码文件数量庞大（544 个），以下基于模块分析和编辑器功能总结核心可用 API。

### 核心资产类型

| 资产类型 | 说明 | 模块 |
|---|---|---|
| `MetaHumanFaceFittingSolver` | 面部拟合求解器配置资产 | `MetaHumanFaceFittingSolver` |
| `MetaHumanIdentity` | MetaHuman 身份资产，存储面部特征数据 | `MetaHumanIdentity` |
| `MetaHumanPerformance` | 表演数据资产 | `MetaHumanPerformance` |

### 编辑器节点（MetaHumanFaceFittingSolverEditor）

该编辑器模块提供了以下资产定义和自定义：

| 功能 | 说明 | 所在类 |
|---|---|---|
| 资产创建工厂 | 在编辑器中创建新的 FaceFittingSolver 资产 | `UMetaHumanFaceFittingSolverFactoryNew` |
| 资产定义 | 定义资产在内容浏览器中的显示名称、颜色、分类 | `UAssetDefinition_MetaHumanFaceFittingSolver` |
| 细节面板自定义 | 自定义 FaceFittingSolver 的属性面板布局 | `FMetaHumanFaceFittingSolverCustomization` |

### 使用流程

1. **创建 MetaHuman Identity**：在内容浏览器中右键 → MetaHuman → Identity
2. **导入捕获数据**：将 iPhone 录制的 .mha 文件或视频素材拖入 UE
3. **配置 FaceFittingSolver**：创建 FaceFittingSolver 资产并配置拟合参数
4. **执行追踪与拟合**：运行面部追踪和拟合流程
5. **生成动画**：使用 AnimationSolver 生成最终动画序列
6. **导出到 Sequencer**：将动画导出为 Level Sequence

## C++ 用法

### 核心模块集成

#### FaceFittingSolver 资产创建

```cpp
// 头文件引入
#include "MetaHumanFaceFittingSolver.h"

// 从 MetaHumanFaceFittingSolverFactoryNew.h 提取的工厂模式
// FactoryCreateNew 实现创建新的 FaceFittingSolver 对象
UObject* Solver = NewObject<UMetaHumanFaceFittingSolver>(InParent, InClass, InName, InFlags);
```

#### 资产定义注册

```cpp
// 从 AssetDefinition_MetaHumanFaceFittingSolver.h 提取
// 自定义资产在内容浏览器中的展示
class UAssetDefinition_MetaHumanFaceFittingSolver : public UAssetDefinitionDefault
{
    virtual FText GetAssetDisplayName() const override;      // 显示名称
    virtual FLinearColor GetAssetColor() const override;      // 内容浏览器中的颜色
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;  // 关联的资产类
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override; // 右键菜单分类
};
```

#### 细节面板自定义

```cpp
// 从 MetaHumanFaceFittingSolverCustomizations.h 提取
#include "IDetailCustomization.h"

class FMetaHumanFaceFittingSolverCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance();
    virtual void CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder) override;
};

// 注册自定义（通常在模块 StartupModule 中）
FPropertyEditorModule& PropertyModule = 
    FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    UMetaHumanFaceFittingSolver::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(
        &FMetaHumanFaceFittingSolverCustomization::MakeInstance
    )
);
```

### 进阶用法

#### 集成多个子系统

```cpp
// 完整的动画流程需要集成多个模块
#include "MetaHumanIdentity.h"
#include "MetaHumanPerformance.h"
#include "MetaHumanFaceContourTracker.h"
#include "MetaHumanFaceFittingSolver.h"
#include "MetaHumanFaceAnimationSolver.h"

// 1. 加载身份资产
UMetaHumanIdentity* Identity = LoadObject<UMetaHumanIdentity>(nullptr, 
    TEXT("/Game/MetaHumans/MyCharacter/Identity_MyCharacter"));

// 2. 加载表演数据
UMetaHumanPerformance* Performance = LoadObject<UMetaHumanPerformance>(nullptr,
    TEXT("/Game/MetaHumans/MyCharacter/Perf_MyCharacter"));

// 3. 配置追踪器并执行追踪
// 4. 使用 FittingSolver 拟合
// 5. 使用 AnimationSolver 生成最终动画
```

## 模块依赖

该插件各模块间存在复杂依赖关系，以下是使用者需要关注的**独特依赖**：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（外部二进制库） |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器接口 |
| `ControlRigDeveloper` | ControlRig 开发者工具，用于面部骨骼控制 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格通用工具 |
| `MetaHumanImageViewerEditor` | 图像查看器，被 CaptureDataEditor 依赖 |

> 无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **维护状态**：🟢 **活跃维护**
- **创建时间**：约 4 年前（2022 年），属于较新的插件
- **更新频率**：非常活跃，最近一周内有多次提交
- **更新内容**：持续的功能增强（身体追踪集成、动画序列导出改进）和 Bug 修复（渲染问题、Sequencer 缓存）
- **官方支持**：Epic Games 官方维护，与 MetaHuman Creator 深度集成
- **推荐使用**：✅ **强烈推荐** — 这是 MetaHuman 角色动画制作的官方标准工具，功能完善且持续迭代

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)（MetaHuman Animator 官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)（MetaHumanControlsConversionTest 模块）