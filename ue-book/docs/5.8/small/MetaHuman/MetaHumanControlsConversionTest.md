# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman 角色资产、动画数据） |
| 模块 | `MetaHumanAnimator` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 角色创建和动画工具包。它解决的核心问题是：如何将真实人物的面部捕捉数据（来自 iPhone TrueDepth 摄像头、其他深度摄像头或视频素材）转换为高质量的 MetaHuman 角色动画。

这个插件的功能远超简单的动画导入，它包含完整的面部捕捉流水线：
- **面部识别与追踪**：从视频中检测和追踪面部关键点
- **深度图生成**：从单目视频生成深度信息
- **面部拟合**：将捕捉的面部形状适配到 MetaHuman 模板
- **动画解算**：将追踪数据转换为面部骨骼动画
- **控制转换**：在不同控制格式之间转换动画数据（如 solve controls → rig controls）
- **语音驱动面部**：从音频生成面部动画（Speech2Face）
- **批量处理**：支持批量处理多个角色或片段

## 使用场景

- 你用 iPhone 拍摄了面部表演片段 → 用 MetaHuman CaptureSource 导入并转换为 MetaHuman 动画
- 你有一段视频素材想转换为 3D 面部动画 → 用 MetaHuman Pipeline 处理
- 你需要为 MetaHuman 角色生成口型同步动画 → 用 MetaHuman Speech2Face
- 你有多个角色的捕捉数据需要批量处理 → 用 MetaHuman BatchProcessor
- 你需要在不同的面部控制格式之间转换动画数据 → 用 MetaHuman Controls Conversion

## 蓝图用法

> **注意**：此插件主要面向编辑器工作流，蓝图 API 较少。核心功能通过编辑器工具和命令行调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMetaHumanFromCapture` | 从捕捉数据创建 MetaHuman | `UMetaHumanIdentity` |
| `SolveFaceAnimation` | 解算面部动画 | `UMetaHumanFaceAnimationSolver` |
| `GenerateDepthMap` | 从视频生成深度图 | `UMetaHumanDepthGenerator` |
| `ConvertFaceControls` | 转换面部控制格式 | `UMetaHumanFaceFittingSolver` |

### 使用示例（蓝图描述）

MetaHuman Animator 的典型工作流在编辑器中完成：

1. 在 Content Browser 中右键 → Animation → MetaHuman Identity
2. 导入 iPhone 捕捉的 .mdat 文件
3. 在 MetaHuman Identity 编辑器中配置面部追踪参数
4. 执行解算生成动画数据
5. 将动画应用到 MetaHuman 角色

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanFaceFittingSolver.h"
#include "MetaHumanPipeline.h"
#include "MetaHumanCaptureUtils.h"
```

### 基本用法

从测试用例中提取的控制格式转换示例：

```cpp
// 来源: Source/MetaHumanControlsConversionTest/Private/Tests/ControlsTestData.h
// MetaHuman 面部控制命名格式: CTRL_{位置}_{部位}_{特征}.{轴向}
// 位置: L(左) R(右) C(中)
// 轴向: tx(X轴) ty(Y轴)

// 输入数据格式 (Solve Controls)
TMap<FString, float> InputSolveControls = {
    {"CTRL_L_brow_down.ty", 0.196608633f},
    {"CTRL_R_brow_down.ty", 0.173116893f},
    {"CTRL_L_brow_lateral.ty", 0.300757229f},
    {"CTRL_L_eye_blink.ty", 0.0349351168f},
    {"CTRL_C_mouth.tx", 0.0331877470f},
    {"CTRL_C_jaw.ty", 0.0826545358f},
    // ... 更多控制
};

// 输出数据格式 (Rig Controls)
TMap<FString, float> ExpectedRigControls = {
    {"CTRL_expressions_browDownL", 0.196609f},
    {"CTRL_expressions_browDownR", 0.173117f},
    {"CTRL_expressions_browLateralL", 0.300757f},
    {"CTRL_expressions_eyeBlinkL", 0.0349351f},
    {"CTRL_expressions_mouthLeft", 0.0331877f},
    {"CTRL_expressions_jawOpen", 0.0826545f},
    // ... 更多控制
};
```

### 进阶用法

从 DNA 文件生成控制映射数据：

```cpp
// 来源: Source/MetaHumanControlsConversionTest/Private/Tests/ConversionDataGenerator.h
#include "ConversionDataGenerator.h"

// 从 DNA 文件提取控制映射信息并写入文件
// 这用于生成测试数据或调试控制转换逻辑
void GenerateMappingsData(const FString& InDnaFilePath, const FString& InOutputPath)
{
    // 写入映射信息
    WriteMappingsInfoFromDnaToFile(InOutputPath);
    
    // DNA 文件包含:
    // - 面部骨骼层次结构
    // - 控制器定义和映射关系
    // - 混合形状权重
    // - 蒙皮权重
}
```

## Demo 示例

```cpp
// MetaHumanControlConversionTest.h
#pragma once

#include "CoreMinimal.h"

class FMetaHumanControlConversionDemo
{
public:
    /** 
     * 演示面部控制格式转换
     * Solve Controls: CTRL_{部位}_{特征}.{轴向}
     * Rig Controls: CTRL_expressions_{特征}{部位}
     */
    static void DemoControlConversion()
    {
        // 定义输入的 Solve 控制数据
        // 这些数据通常来自面部追踪解算器
        TMap<FString, float> SolveControls;
        SolveControls.Add("CTRL_L_brow_down.ty", 0.2f);
        SolveControls.Add("CTRL_R_brow_down.ty", 0.18f);
        SolveControls.Add("CTRL_L_eye_blink.ty", 0.035f);
        SolveControls.Add("CTRL_R_eye_blink.ty", 0.037f);
        SolveControls.Add("CTRL_C_jaw.ty", 0.08f);
        SolveControls.Add("CTRL_C_mouth.tx", 0.03f);
        
        // 转换为 Rig 控制格式
        // Rig 控制器用于驱动最终的 MetaHuman 骨骼动画
        TMap<FString, float> RigControls;
        
        for (const auto& Pair : SolveControls)
        {
            FString RigControlName = ConvertToRigControlName(Pair.Key);
            if (!RigControlName.IsEmpty())
            {
                RigControls.Add(RigControlName, Pair.Value);
            }
        }
        
        // 验证转换结果
        // 例如: CTRL_L_brow_down.ty -> CTRL_expressions_browDownL
        verify(RigControls.Contains("CTRL_expressions_browDownL"));
        verify(FMath::IsNearlyEqual(RigControls["CTRL_expressions_browDownL"], 0.2f, 0.001f));
    }

private:
    /** 将 Solve 控制名称转换为 Rig 控制名称 */
    static FString ConvertToRigControlName(const FString& InSolveName)
    {
        // 解析格式: CTRL_{位置}_{部位}_{特征}.{轴向}
        // 转换为: CTRL_expressions_{特征}{位置}
        
        FString Name = InSolveName;
        
        // 移除轴向后缀 (.tx, .ty)
        int32 DotIndex;
        if (Name.FindChar('.', DotIndex))
        {
            Name = Name.Left(DotIndex);
        }
        
        // 移除 CTRL_ 前缀
        Name.RemoveFromStart("CTRL_");
        
        // 解析位置和部位
        FString Location, Rest;
        if (Name.Split("_", &Location, &Rest))
        {
            // 转换为驼峰命名
            FString RigName = "CTRL_expressions_";
            
            // 添加特征名（首字母小写）
            RigName += Rest;
            
            // 添加位置后缀 (L/R/C)
            if (Location == "L")
            {
                RigName += "L";
            }
            else if (Location == "R")
            {
                RigName += "R";
            }
            
            return RigName;
        }
        
        return FString();
    }
};
```

## 模块依赖

此插件包含 29 个模块，以下列出主要的非标准依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（DNA 处理、面部解算） |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器集成 |
| `ControlRigDeveloper` | Control Rig 开发者工具（用于骨骼控制） |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格工具（用于蒙皮权重处理） |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器（用于查看捕捉素材） |
| `MetaHumanCaptureDataEditor` | 捕捉数据编辑器（依赖 ImageViewerEditor） |

**注意**：此插件大部分模块标记为 Runtime，但实际上主要在编辑器中使用。许多 Editor 后缀的模块提供编辑器 UI 和工具。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH | 修复 MetaHuman 渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护中** ⚡

这是 Epic Games 官方维护的核心插件，具有以下特点：

1. **持续更新**：最近一周内有多次提交，专注于功能改进和 Bug 修复
2. **功能完善**：包含完整的面部捕捉、追踪、解算、动画生成工作流
3. **代码规模大**：544 个源文件，29 个模块，说明功能非常全面
4. **企业级质量**：有专门的测试模块（MetaHumanControlsConversionTest）验证控制转换逻辑
5. **跨平台支持**：支持 Win64、Linux、Mac

**推荐使用**：这是创建 MetaHuman 角色的官方工具，是使用 MetaHuman 角色的必经之路。虽然主要面向专业用户和高端制作，但 Epic 持续投入资源维护和改进。

**注意事项**：
- 插件默认未启用，需要在 Plugins 面板手动启用
- 需要较大的存储空间（MetaHuman 角色资产通常较大）
- 面部捕捉功能需要 iPhone 或其他深度摄像头硬件
- 初始学习曲线较陡，建议参考 Epic 官方教程

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-in-unreal-engine/)（MetaHuman Animator 官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)