# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、UI 资产、测试数据） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanPlatform` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-05-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 面部动画工具链。它解决的核心问题是：**如何将真实演员的面部表演（通过 iPhone TrueDepth 摄像头或专业动捕设备采集）转换为 MetaHuman 角色的高质量面部动画**。

整个工具链覆盖了从原始视频采集到最终动画输出的完整流程：

1. **采集**：通过 Live Link Face（iPhone）或专业动捕设备采集面部表演数据（视频 + 深度信息）
2. **追踪**：从视频中检测和追踪面部轮廓关键点
3. **求解**：将追踪结果转换为面部动画控制参数（Solve Controls）
4. **控制转换**：将 Solve Controls 映射到 MetaHuman 骨骼绑定系统（Rig Controls），这是两个不同控制空间之间的转换
5. **拟合**：将动画适配到特定 MetaHuman 角色的面部网格
6. **输出**：通过 Sequencer 集成将动画序列化输出，或通过 Pipeline 批量处理

此外，还支持语音驱动面部动画（Speech2Face）和批量处理（BatchProcessor）等高级功能。

## 使用场景

- 你有 iPhone（支持 Face ID）并想为 MetaHuman 角色录制面部动画 → 使用 MetaHuman Animator 的捕获功能
- 你有专业动捕设备（如 Cubic Motion）的数据需要导入 → 使用 MetaHumanCaptureSource 配合 CaptureProtocolStack
- 你已有一段面部表演视频，想驱动 MetaHuman → 使用 FootageIngest 导入后走完整流程
- 你需要批量处理大量面部动画数据 → 使用 MetaHumanBatchProcessor
- 你想用语音驱动面部动画 → 使用 MetaHumanSpeech2Face
- 你需要将录制好的面部动画精确映射到自定义 MetaHuman → 使用 MetaHumanIdentity 管理角色身份，配合 FaceFittingSolver 进行拟合
- 你需要在 Sequencer 中编辑面部动画曲线 → 使用 MetaHumanSequencer 模块

## 蓝图用法

本插件主要面向编辑器工作流，大部分功能通过编辑器面板操作。以下是从源码中提取的可蓝图调用接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreatePerformance` | 从捕获数据创建面部表演资源 | `UMetaHumanPerformance` |
| `StartCapture` | 启动面部捕获会话 | `UMetaHumanCaptureSource` |
| `ImportFootage` | 导入外部视频素材作为捕获数据 | `UMetaHumanFootageIngest` |
| `SolveFaceAnimation` | 对捕获数据运行面部动画求解 | `UMetaHumanFaceAnimationSolver` |
| `FitToIdentity` | 将动画拟合到指定 MetaHuman 身份 | `UMetaHumanFaceFittingSolver` |
| `ExportToSequence` | 将求解结果导出为动画序列 | `UMetaHumanSequencer` |
| `ProcessBatch` | 批量处理多个表演数据 | `UMetaHumanBatchProcessor` |

### 使用示例（蓝图描述）

典型的面部动画工作流程：

1. 在 Content Browser 中右键 → Animation → MetaHuman Performance，创建一个 Performance 资产
2. 在 Performance 编辑器面板中导入捕获数据（.mha 文件或视频文件）
3. 点击 "Solve" 按钮运行面部追踪和动画求解
4. 选择目标 MetaHuman Identity 资产，执行面部拟合
5. 使用 "Export to Level Sequence" 将结果输出到 Sequencer

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanPerformance.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanPipeline.h"
```

### 基本用法

以下代码展示了面部动画求解控制（Solve Controls）到骨骼绑定控制（Rig Controls）的核心转换逻辑，基于测试数据验证：

```cpp
// 来源: Source/MetaHumanControlsConversionTest/Private/Tests/ControlsTestData.h
// MetaHuman Animator 内部使用两套控制命名系统:
// 1. Solve Controls - 面部求解器输出的原始控制值（如 CTRL_L_brow_down.ty）
// 2. Rig Controls - MetaHuman 骨骼绑定使用的控制值（如 CTRL_expressions_browDownL）

// Solve Controls 示例（求解器输出格式）
TMap<FString, float> SolveControls;
SolveControls.Add("CTRL_L_brow_down.ty", 0.196608633f);
SolveControls.Add("CTRL_R_brow_down.ty", 0.173116893f);
SolveControls.Add("CTRL_L_eye_blink.ty", 0.0349351168f);
SolveControls.Add("CTRL_R_eye_blink.ty", 0.0373136997f);
SolveControls.Add("CTRL_C_jaw.ty", 0.0826545358f);
SolveControls.Add("CTRL_C_mouth.tx", 0.0331877470f);
SolveControls.Add("CTRL_C_tongue_move.ty", -0.257301092f);

// 对应的 Rig Controls（骨骼绑定格式）
TMap<FString, float> RigControls;
RigControls.Add("CTRL_expressions_browDownL", 0.196609f);       // 眉毛下压（左）
RigControls.Add("CTRL_expressions_browDownR", 0.173117f);       // 眉毛下压（右）
RigControls.Add("CTRL_expressions_eyeBlinkL", 0.0349351f);      // 眨眼（左）
RigControls.Add("CTRL_expressions_eyeBlinkR", 0.0373137f);      // 眨眼（右）
RigControls.Add("CTRL_expressions_jawOpen", 0.0826545f);        // 下巴张开
RigControls.Add("CTRL_expressions_mouthLeft", 0.0331877f);      // 嘴巴左移
RigControls.Add("CTRL_expressions_tongueDown", 0.257301f);      // 舌头向下
```

### 进阶用法

控制参数涵盖面部的完整解剖结构，支持精细控制：

```cpp
// 来源: Source/MetaHumanControlsConversionTest/Private/Tests/ControlsTestData.h

// 面部控制参数的完整分类:

// 1. 眉毛区域 (Brow)
// CTRL_expressions_browDownL/R      - 眉毛下压
// CTRL_expressions_browLateralL/R   - 眉毛横向移动
// CTRL_expressions_browRaiseInL/R   - 内侧眉毛上扬
// CTRL_expressions_browRaiseOuterL/R - 外侧眉毛上扬

// 2. 眼部区域 (Eye)
// CTRL_expressions_eyeBlinkL/R      - 眨眼
// CTRL_expressions_eyeSquintInnerL/R - 内眼角眯眼
// CTRL_expressions_eyeCheekRaiseL/R - 面颊提升
// CTRL_expressions_eyeLookDownL/R   - 向下看（y 方向映射）
// CTRL_expressions_eyePupilWideL/R  - 瞳孔放大

// 3. 鼻子区域 (Nose)
// CTRL_expressions_noseWrinkleL/R          - 鼻子皱纹
// CTRL_expressions_noseNostrilDilateL/R    - 鼻孔扩张（tx→Dilate 映射）
// CTRL_expressions_noseNostrilDepressL/R   - 鼻孔下压（ty→Depress 映射）
// CTRL_expressions_noseNasolabialDeepenL/R - 法令纹加深

// 4. 嘴部区域 (Mouth) - 最复杂的区域，约 80+ 个控制参数
// CTRL_expressions_mouthCornerPullL/R     - 嘴角上拉（微笑）
// CTRL_expressions_mouthCornerDepressL/R  - 嘴角下压
// CTRL_expressions_mouthUpperLipRaiseL/R  - 上唇提升
// CTRL_expressions_mouthLipsPurseDL/R     - 嘟嘴（下方）
// CTRL_expressions_mouthLipsPullDL/R      - 嘴唇内拉（下方）
// CTRL_expressions_mouthFunnelUL/DL       - 嘴唇漏斗状
// CTRL_expressions_mouthStretchL/R        - 嘴唇拉伸

// 5. 下巴/下颌区域 (Jaw)
// CTRL_expressions_jawOpen          - 张嘴
// CTRL_expressions_jawLeft/Right    - 下巴左右移动
// CTRL_expressions_jawFwd           - 下巴前伸
// CTRL_expressions_jawChinRaiseDL/R - 下巴提升

// 6. 舌头区域 (Tongue)
// CTRL_expressions_tongueUp/Down     - 舌头上下
// CTRL_expressions_tongueLeft/Right  - 舌头左右
// CTRL_expressions_tongueIn/Out      - 舌头进出
// CTRL_expressions_tongueWide/Narrow - 舌头宽窄
// CTRL_expressions_tonguePress       - 舌头按压
// CTRL_expressions_tongueThick/Thin  - 舌头厚薄
// CTRL_expressions_tongueRoll        - 舌头卷曲
// CTRL_expressions_tongueTipUp/Down  - 舌尖上下

// 7. 脖子区域 (Neck)
// CTRL_expressions_neckDigastricUp/Down   - 颈部二腹肌
// CTRL_expressions_neckMastoidContractL/R - 胸锁乳突肌收缩
// CTRL_expressions_neckSwallowPh1-4       - 吞咽动作（4个阶段）

// 注意: 部分 Solve Controls 需要符号反转（如 pushPull 的负值）
// Solve 中的 pushPullU 值为负 → Rig 中 lipsPullU 为正（取绝对值）
SolveControls.Add("CTRL_L_mouth_pushPullU.ty", -0.108609557f);
RigControls.Add("CTRL_expressions_mouthLipsPullUL", 0.10861f);   // 反转符号
```

## Demo 示例

以下示例展示如何在 C++ 中创建并查询面部表演数据：

```cpp
// MetaHumanPerformanceDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanPerformanceDemo.generated.h"

UCLASS()
class AMetaHumanPerformanceDemo : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanPerformanceDemo();

    /** 加载并查询面部表演数据 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void LoadPerformanceData(const FString& InPerformancePath);

    /** 从求解控制获取 Rig 控制值 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    float GetRigControlValue(const FString& InControlName) const;

protected:
    /** 已加载的 Rig 控制值缓存 */
    UPROPERTY()
    TMap<FString, float> CachedRigControls;
};
```

```cpp
// MetaHumanPerformanceDemo.cpp
#include "MetaHumanPerformanceDemo.h"
#include "MetaHumanPerformance.h"
#include "MetaHumanFaceAnimationSolver.h"

AMetaHumanPerformanceDemo::AMetaHumanPerformanceDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanPerformanceDemo::LoadPerformanceData(const FString& InPerformancePath)
{
    // 加载 MetaHuman Performance 资产
    UMetaHumanPerformance* Performance = LoadObject<UMetaHumanPerformance>(
        nullptr, *InPerformancePath);

    if (!Performance)
    {
        UE_LOG(LogTemp, Error, TEXT("无法加载 Performance: %s"), *InPerformancePath);
        return;
    }

    // 此处演示的是控制值映射的概念
    // 实际工作流中，MetaHumanPipeline 会自动处理
    // Solve Controls → Rig Controls 的转换
    UE_LOG(LogTemp, Log, TEXT("已加载 Performance: %s"), *Performance->GetName());
}

float AMetaHumanPerformanceDemo::GetRigControlValue(const FString& InControlName) const
{
    const float* Value = CachedRigControls.Find(InControlName);
    return Value ? *Value : 0.0f;
}
```

## 模块依赖

本插件拥有 28 个模块，模块间的依赖关系较为复杂。以下列出非标准的、具有该插件特色的依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库（外部依赖） |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器接口 |
| `ControlRigDeveloper` | Control Rig 开发者工具，用于面部骨骼绑定系统 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格通用工具，用于面部网格处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **维护状态**：🟢 **活跃维护中** — 最近更新在 2026 年 5 月，且持续有功能性更新和 bug 修复
- **开发团队**：Epic Games 官方维护，是 MetaHuman 生态的核心组件
- **更新频率**：非常活跃，几乎每天都有提交，包含功能增强和问题修复
- **成熟度**：已从实验性功能演进为正式工具链（非 Beta，非 Experimental），版本号已达 5.0.0
- **已知限制**：主要面向 Windows 平台开发（iPhone 捕获需要 macOS 中转），Linux/Mac 支持可能有限
- **推荐程度**：⭐⭐⭐⭐⭐ **强烈推荐** — 这是 MetaHuman 面部动画的官方标准工具，无替代方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-in-unreal-engine/)（MetaHuman Animator 官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest/Private/Tests)