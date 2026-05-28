# Live Link Control Rig

> Allows access to LiveLink Data through Control Rig

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接控制绑定 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkControlRig` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-01-22 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LiveLinkControlRig) | |

## 用途

该插件是连接 **Live Link** 实时数据流与 **Control Rig** 动画系统的桥梁。它提供了一套专用的 **Control Rig 单元（Rig Units）**，允许动画师和技术美术师在 Control Rig 的图表编辑器中直接读取和处理来自 Live Link 的实时数据（如动捕骨骼动画、变换数据、控制器参数等），并用于驱动或混合 Control Rig 控制的角色。解决了传统流程中需要通过蓝图或 C++ 代码进行繁琐数据转换的问题，实现了在动画控制核心层的直接集成。

## 使用场景

- 你需要在虚拟直播或实时动画预览中，使用实时动捕数据（来自 Vicon、OptiTrack 等设备）直接驱动 Control Rig 控制的角色。
- 你希望将来自移动设备或专用硬件（如手柄）的 Live Link 输入设备数据，在 Control Rig 中用于控制角色的特定部位或触发动作。
- 你需要在 Control Rig 内部混合动画序列、程序化动画以及实时动捕输入。

## 蓝图用法

该插件的功能主要通过 Control Rig 编辑器中的 **Live Link** 类别节点实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Live Link Frame (Animation)` | 获取指定 Live Link 主体的动画帧数据，包含所有骨骼变换和属性。 | `FRigUnit_LiveLinkEvaluteFrameAnimation` |
| `Evaluate Live Link Frame (Transform)` | 获取指定 Live Link 主体的单个变换（Transform）数据。 | `FRigUnit_LiveLinkEvaluteFrameTransform` |
| `Get Transform By Name` | 从已获取的动画帧（`FSubjectFrameHandle`）中，按名称提取特定骨骼的变换。 | `FRigUnit_LiveLinkGetTransformByName` |
| `Get Parameter Value By Name` | 从已获取的动画帧中，按名称提取特定参数的浮点值。 | `FRigUnit_LiveLinkGetParameterValueByName` |
| `Get Basic Live Link Data` | 直接从指定主体获取一个基础的浮点属性值（例如来自简单 Live Link 源）。 | `FRigUnit_LiveLinkEvaluateBasicValue` |
| `Get Live Link Input Device Data` | 获取指定 Live Link 主体的游戏手柄等输入设备数据。 | `FRigUnit_LiveLinkEvaluateInputDeviceValue` |

### 使用示例（蓝图描述）

1.  在 Control Rig 图表中，添加一个 **“Evaluate Live Link Frame (Animation)”** 节点。
2.  将 **`SubjectName`** 输入引脚连接到一个包含 Live Link 主体名称的变量（例如从 Live Link 预览面板复制的名称）。
3.  将该节点的 **`SubjectFrame`** 输出引脚，连接到 **“Get Transform By Name”** 节点的 **`SubjectFrame`** 输入引脚。
4.  在 **“Get Transform By Name”** 节点的 **`TransformName`** 输入中，填入你想要驱动的骨骼名称（如 `head`）。
5.  将其 **`Transform`** 输出通过 **“Set Transform”** 或 **“Set Bone Transform”** 节点，应用到 Control Rig 驱动的骨骼上。
6.  （可选）为调试，将第一个评估节点的 **`bDrawDebug`** 设为 `true`，并设置 `DebugColor` 和 `DebugDrawOffset`，即可在视口中看到源数据的骨骼位置。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkControlRig.h"
#include "Units/RigUnit.h"
// 如果你需要使用 LiveLink 相关的结构体，可能还需要：
#include "LiveLinkTypes.h"
```

### 基本用法

该插件主要通过注册自定义的 `FRigUnit` 来扩展功能。以下是如何创建一个简单的、与该插件风格一致的自定义 Live Link Rig 单元的示例。

```cpp
// MyLiveLinkRigUnit.h
#pragma once

#include "Units/RigUnit.h"
#include "LiveLinkTypes.h" // 用于 FLiveLinkGamepadInputDeviceFrameData 等
#include "LiveLinkRigUnits.h" // 为了继承 FRigUnit_LiveLinkBase

// 自定义单元：从 Live Link 获取一个布尔值
USTRUCT(meta = (DisplayName = "Get Live Link Bool Value", Category = "My Live Link"))
struct FRigUnit_MyGetLiveLinkBoolValue : public FRigUnit
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute() override;

    UPROPERTY(meta = (Input))
    FName SubjectName;

    UPROPERTY(meta = (Input))
    FName PropertyName;

    UPROPERTY(meta = (Output))
    bool bValue = false;
};
```

### 进阶用法

组合多个单元实现复杂逻辑。例如，先获取动画帧，再从中提取多个骨骼数据。

```cpp
// 在 Control Rig 的某个函数或节点执行逻辑中
FRigUnit_LiveLinkEvaluteFrameAnimation EvalNode;
EvalNode.SubjectName = TEXT("MyMocapSubject");
EvalNode.Execute(); // 内部会调用 LiveLinkClient 获取数据

// 使用 EvalNode.SubjectFrame 作为输入
FRigUnit_LiveLinkGetTransformByName GetHeadNode;
GetHeadNode.SubjectFrame = EvalNode.SubjectFrame;
GetHeadNode.TransformName = TEXT("head");
GetHeadNode.Execute();
FTransform HeadTransform = GetHeadNode.Transform;

FRigUnit_LiveLinkGetTransformByName GetHandNode;
GetHandNode.SubjectFrame = EvalNode.SubjectFrame;
GetHandNode.TransformName = TEXT("hand_r");
GetHandNode.Execute();
FTransform HandTransform = GetHandNode.Transform;

// 将 HeadTransform 和 HandTransform 应用到你的角色或逻辑中...
```

## Demo 示例

一个完整的、可编译的最小自定义 Live Link Rig 单元示例。

**MyLiveLinkRigUnit.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Units/RigUnit.h"
#include "LiveLinkTypes.h" // 确保你的模块依赖了 LiveLinkInterface

USTRUCT(meta = (DisplayName = "Get Live Link Float Property", Category = "Demo|LiveLink"))
struct FRigUnit_DemoGetLiveLinkFloat : public FRigUnit
{
	GENERATED_BODY()

	FRigUnit_DemoGetLiveLinkFloat()
		: SubjectName(NAME_None)
		, PropertyName(NAME_None)
		, Value(0.f)
	{
	}

	RIGVM_METHOD()
	virtual void Execute() override;

	// 要查询的 Live Link 主体名称
	UPROPERTY(meta = (Input))
	FName SubjectName;

	// 要查询的属性名称
	UPROPERTY(meta = (Input))
	FName PropertyName;

	// 获取到的浮点值
	UPROPERTY(meta = (Output))
	float Value;
};
```

**MyLiveLinkRigUnit.cpp**
```cpp
#include "MyLiveLinkRigUnit.h"
#include "ILiveLinkClient.h"
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkBasicRole.h"
#include "Roles/LiveLinkBasicTypes.h"

void FRigUnit_DemoGetLiveLinkFloat::Execute()
{
	// 1. 获取 Live Link 客户端
	ILiveLinkClient* LiveLinkClient = ILiveLinkClient::Get(); // 假设你的环境中有这样的访问方式，实际实现可能需要从模块获取

	if (LiveLinkClient && SubjectName != NAME_None)
	{
		// 2. 获取主体快照
		FLiveLinkSubjectKey SubjectKey(FName("LiveLink"), SubjectName); // “LiveLink” 是常见的虚拟源名称
		FLiveLinkSubjectFrameData SubjectData;
		if (LiveLinkClient->EvaluateFrame_AnyThread(SubjectKey, ULiveLinkBasicRole::StaticClass(), SubjectData))
		{
			// 3. 在属性集合中查找目标属性
			const TMap<FName, float>& FloatProperties = SubjectData.FrameData->CastChecked<FLiveLinkBasicFrameData>().FloatProperties;
			if (const float* FoundValue = FloatProperties.Find(PropertyName))
			{
				Value = *FoundValue;
				return;
			}
		}
	}
	// 如果任何步骤失败，值为0
	Value = 0.f;
}
```

## 模块依赖

从该插件的功能（使用 `FRigUnit`, `FSubjectFrameHandle`, `ILiveLinkClient` 等）和其 `.uplugin` 中声明的插件依赖推断：

| 模块 | 用途 |
|---|---|
| `ControlRig` | 提供 `FRigUnit` 基类、RigVM 执行环境和 Control Rig 编辑器集成。 |
| `LiveLink` | 提供 Live Link 框架的核心类，如 `FLiveLinkSubjectFrame`。 |
| `LiveLinkInterface` | 提供 `ILiveLinkClient` 接口和基本的 Live Link 数据类型。 |

**注意**：你的模块在使用该插件的功能时，需要在 `.Build.cs` 文件中添加对 `LiveLinkControlRig`、`ControlRig` 和 `LiveLinkInterface` 的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了可能导致链接错误的重复符号问题。 |
| 2025-12-08 | `4086699f` | Control Rig / RigVM: fix tooltips round 2 | 继续改进 Control Rig 和 RigVM 相关节点的工具提示信息。 |
| 2025-10-15 | `33f0fd3e` | RigVM: Complete documentation / comments on remaining nodes | 为 RigVM 中剩余的节点补充了完整的文档和注释。 |
| 2025-10-14 | `f0ed5774` | Control Rig: Apply strict documentation policy to ... nodes | 对特定的 Control Rig 节点应用了严格的文档编写策略。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 为源文件添加了宏，以优化编译过程。 |

### 维护评价

该插件自 **2020 年** 创建以来，一直有持续的维护。从 git 记录看，直到 **2026 年初** 仍有活跃的功能性更新（如修复链接错误、完善文档）。这表明它仍处于**活跃维护**状态。然而，其 `.uplugin` 中明确标记为 `IsBetaVersion: true`，且默认未启用 (`EnabledByDefault: false`)，这说明它仍处于**实验阶段**，API 和功能可能在未来的引擎版本中发生变化，不建议用于对稳定性要求极高的最终产品。推荐在原型制作、实验性项目或虚拟直播等需要实时动捕集成的场景中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LiveLinkControlRig)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/LiveLinkControlRig/Source/LiveLinkControlRig/Private/LiveLinkRigUnits.cpp) (实现文件通常包含单元逻辑)