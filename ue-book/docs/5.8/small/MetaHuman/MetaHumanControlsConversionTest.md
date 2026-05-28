# MetaHuman Controls Conversion Test

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 控制转换测试 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试数据） |
| 模块 | `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-06-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Controls Conversion Test 是 MetaHuman Animator 插件中的一个**纯测试模块**，用于验证 MetaHuman 面部动画控制系统（Solve Controls）到最终骨骼控制（Rig Controls）之间的转换逻辑是否正确。

MetaHuman Animator 的面部动画流程涉及多层控制映射：从面部捕捉数据（如 ARKit blend shapes）经过求解器（Solver）生成中间 Solve Controls，再通过转换系统映射到最终的 Rig Controls。这个测试模块专门验证这一步转换的准确性——确保输入的 Solve Controls 值能正确映射到期望的 Rig Controls 值。

该模块包含两组测试数据：
- **SolveControlsTestData**：包含一组真实的面部表情 Solve Controls 输入值及其对应的期望 Rig Controls 输出值，用于回归测试
- **MinControlsTestData**：包含一组最小值（-1.0）的 Solve Controls 输入，用于边界测试

## 使用场景

- **MetaHuman 面部动画开发**：当你在修改面部控制转换逻辑时，运行此测试确保不会破坏现有映射
- **Rig Controls 验证**：当你需要验证 Solve Controls 到 Rig Controls 的映射关系是否正确
- **回归测试**：在修改 MetaHumanAnimator 代码后，确保已知的面部表情数据仍然产生正确结果

## 蓝图用法

本模块是纯测试模块，不包含任何蓝图可调用的 API。

## C++ 用法

### 头文件引入

```cpp
#include "ControlsTestData.h"
```

### 基本用法

测试数据以 `TMap<FString, float>` 的形式存储在命名空间中，直接引用即可：

```cpp
#include "Tests/ControlsTestData.h"

// 使用 SolveControlsTestData 命名空间中的测试数据
const TMap<FString, float>& InputControls = SolveControlsTestData::InputSolveControls;
const TMap<FString, float>& ExpectedControls = SolveControlsTestData::ExpectedRigControls;

// 遍历输入控制并验证转换结果
for (const auto& Pair : InputControls)
{
    const FString& SolveControlName = Pair.Key;   // 例如 "CTRL_L_brow_down.ty"
    const float SolveControlValue = Pair.Value;
    
    // 在此处调用你的转换函数
    // float ConvertedValue = ConvertSolveToRigControl(SolveControlName, SolveControlValue);
    
    // 验证转换结果
    // const float* ExpectedValue = ExpectedControls.Find(ConvertedControlName);
    // if (ExpectedValue)
    // {
    //     TestEqual(TEXT("Control conversion matches"), ConvertedValue, *ExpectedValue, Tolerance);
    // }
}
```

### 测试数据结构说明

测试数据包含 MetaHuman 面部动画系统中两类控制：

**Solve Controls（求解控制）**：
- 格式：`CTRL_{Side}_{Area}_{Action}.{Axis}`
- 示例：`CTRL_L_brow_down.ty`（左侧眉毛下沉，Y轴平移）
- Side：L（左）、R（右）、C（中心）
- Area：brow（眉）、eye（眼）、mouth（嘴）、jaw（下颌）、tongue（舌）、nose（鼻）

**Rig Controls（骨骼控制）**：
- 格式：`CTRL_expressions_{controlName}`
- 示例：`CTRL_expressions_browDownL`（左侧眉毛下沉）

### 进阶用法

参考测试模块的辅助函数 `WriteMappingsInfoFromDnaToFile`：

```cpp
// 从 DNA 文件导出控制映射信息
FString OutputPath = FPaths::ProjectSavedDir() / TEXT("ControlMappings.txt");
WriteMappingsInfoFromDnaToFile(OutputPath);
```

此函数用于从 MetaHuman DNA 文件中提取控制映射信息并写入文件，通常用于调试和生成新的测试参考数据。

## Demo 示例

本模块为测试模块，不提供 Demo。以下是一个基于测试数据的最小验证示例：

```cpp
// MetaHumanControlConversionTestExample.h
#pragma once

#include "CoreMinimal.h"

class FControlConversionExample
{
public:
    /** 验证 Solve Controls 到 Rig Controls 的转换 */
    static bool ValidateConversion(const TMap<FString, float>& InSolveControls,
                                   const TMap<FString, float>& InExpectedRigControls,
                                   float InTolerance = 0.001f);
};
```

```cpp
// MetaHumanControlConversionTestExample.cpp
#include "MetaHumanControlConversionExample.h"
#include "Tests/ControlsTestData.h"

bool FControlConversionExample::ValidateConversion(
    const TMap<FString, float>& InSolveControls,
    const TMap<FString, float>& InExpectedRigControls,
    float InTolerance)
{
    // 在实际使用中，这里需要调用 MetaHumanAnimator 的转换 API
    // 将 Solve Controls 映射为 Rig Controls，然后与期望值比较
    
    for (const auto& Pair : InSolveControls)
    {
        // 模拟转换过程
        // float RigValue = MetaHumanConvertSolveToRig(Pair.Key, Pair.Value);
        
        // 查找期望值
        // const float* Expected = InExpectedRigControls.Find(RigControlName);
        // if (Expected && FMath::Abs(RigValue - *Expected) > InTolerance)
        // {
        //     return false;
        // }
    }
    
    return true;
}
```

## 模块依赖

本模块是 MetaHumanAnimator 插件的纯测试模块，不对外暴露依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | 纯测试数据模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

MetaHumanAnimator 是 Epic Games 官方维护的 MetaHuman 核心工具包，处于**活跃维护**状态。

- **创建时间**：约 2023 年（MetaHuman Animator 随 UE5.2 发布）
- **最近更新**：2026 年 5 月仍有密集的功能更新和 bug 修复
- **活跃度**：非常高，几乎每天都有提交
- **已知限制**：
  - 本测试模块仅包含静态测试数据，不包含自动化测试执行逻辑
  - 测试数据中的控制映射基于特定版本的 MetaHuman DNA 格式，DNA 版本更新后可能需要同步更新测试数据
- **推荐程度**：⭐⭐⭐⭐⭐ 作为 MetaHuman 动画流程的核心验证工具，建议在修改面部控制相关代码后运行此测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-in-unreal-engine/)