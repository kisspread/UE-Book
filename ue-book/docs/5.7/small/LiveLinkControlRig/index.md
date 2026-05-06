# Live Link Control Rig

> Allows access to LiveLink Data through Control Rig

| 属性 | 值 |
|---|---|
| 中文名 | LiveLink 控制绑定 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkControlRig` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkControlRig) | |

## 用途

在 Control Rig（控制装备）中直接访问和评估 LiveLink 数据。Control Rig 是用于驱动角色动画的脚本化节点图，该插件提供了一组专用的 Rig Unit（节点），允许你在 Control Rig 图表中：

- 根据 Subject Name 获取当前的 LiveLink 动画帧（包含骨骼变换、曲线等）
- 从已获取的动画帧中按名称提取特定骨骼的变换（支持局部/世界空间）
- 按名称提取动画帧中的参数值（浮点数、布尔值等）
- 获取 LiveLink 输入设备数据（如游戏手柄的按钮/轴状态）

解决以下问题：在角色动画系统中，LiveLink 数据通常通过蓝图或 C++ 手动处理后再传入 Control Rig，流程繁琐。该插件让你在 Control Rig 内部直接消费 LiveLink 数据，简化动画管线，尤其适用于**动捕驱动角色**、**实时外部设备输入**等场景。

## 使用场景

- **动捕/面部捕捉角色动画**：通过 LiveLink 从动捕系统（如 OptiTrack、Xsens）或面部捕捉设备（如 iPhone）接收实时骨骼数据，在 Control Rig 中直接按名称获取骨骼变换并驱动角色。
- **游戏手柄/外部输入驱动角色**：将游戏手柄的 LiveLink 输入（如按钮、摇杆）映射到 Control Rig 的动画参数（如 BlendSpace 坐标、FK 控制），实现实时交互式动画。
- **混合控制解决方案**：在 Control Rig 中同时使用动捕 LiveLink 数据和传统的动画蓝图逻辑，例如将动捕数据与程序化修正叠加，或仅在特定状态下启用 LiveLink 驱动。

## 蓝图用法

该插件不提供传统的蓝图节点，而是暴露为 Control Rig 中的 Rig Unit 节点。在 Control Rig 图表中右键添加节点时，可在 **Live Link** 类别下找到以下节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Live Link Frame (Animation)` | 根据 Subject Name 从 LiveLink 客户端获取当前有效的动画帧数据，输出 `SubjectFrameHandle` | `FRigUnit_LiveLinkEvaluteFrameAnimation` |
| `Get Transform By Name` | 从已获取的 `SubjectFrameHandle` 中按 `TransformName`（骨骼名称）提取变换值，支持局部/世界空间 | `FRigUnit_LiveLinkGetTransformByName` |
| `Get Parameter Value By Name` | 从 `SubjectFrameHandle` 中按参数名称提取 `FRigUnit_LiveLinkBase` 子类中定义的参数值（如浮点数、布尔值） | `FRigUnit_LiveLinkGetParameterValueByName` |
| `Get Live Link Input Device Data` | 根据 Subject Name 直接获取当前帧的 `FLiveLinkGamepadInputDeviceFrameData`（包含按钮、轴数据），无需先评估动画帧 | `FRigUnit_LiveLinkEvaluateInputDeviceValue` |

### 使用示例（蓝图描述）

**例：实时获取动捕骨骼旋转**

1. 在 Control Rig 图表中添加 **Evaluate Live Link Frame (Animation)** 节点
2. 将 `SubjectName` 设置为你的动捕主体名称（例如 "MotionCaptureSubject"）
3. 从该节点的 `SubjectFrame` 引脚拖出一条线，连接到 **Get Transform By Name** 节点的 `SubjectFrame` 输入
4. 设置 `TransformName` 为 "hand_r"（右手的骨骼名称），`Space` 选择 "LocalSpace"
5. 输出 `Transform` 连接到角色的 `FK` 骨骼控制器或 `Hierarchy` 修改器

**例：读取游戏手柄输入并驱动角色参数**

1. 确保 LiveLink 接收了游戏手柄输入（使用 `LiveLinkInputDevice` 角色）
2. 添加 **Get Live Link Input Device Data** 节点，`SubjectName` 设置为游戏手柄的 Subject 名称
3. 输出 `InputDeviceData` 包含 `LeftAnalogY`、`RightTrigger` 等字段
4. 将这些字段值连接到 Control Rig 的 `AimOffset` 或 `BlendSpace` 参数上

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkRigUnits.h"           // 动画帧评估、变换提取、参数提取
#include "LiveLinkInputDeviceRigUnits.h" // 输入设备数据评估
```

### 基本用法

以下示例展示如何在自定义 Control Rig 子类中手动执行这些 Rig Unit，通常你只需要在 Control Rig 图表中连接节点即可，但 C++ 中也可以直接调用。

```cpp
// 来源：LiveLinkControlRig/Source/LiveLinkControlRig/Private/LiveLinkRigUnits.cpp（推断）
// 注意：这些 Rig Unit 通常由 RIGVM 调用，无需手动实例化

// 1. 获取 LiveLink 客户端（辅助函数）
ILiveLinkClient* LiveLinkClient = LiveLinkControlRigUtilities::TryGetLiveLinkClient();
if (!LiveLinkClient) return;

// 2. 构造 Evaluate 节点并执行（伪代码，实际通过控制装备上下文）
FRigUnit_LiveLinkEvaluteFrameAnimation EvalUnit;
EvalUnit.SubjectName = FName("MySubject");
EvalUnit.Execute(LiveLinkClient, Context); // 假设有合适上下文

// 3. 从帧中获取骨骼变换
FRigUnit_LiveLinkGetTransformByName TransformUnit;
TransformUnit.SubjectFrame = EvalUnit.SubjectFrame;
TransformUnit.TransformName = FName("hand_r");
TransformUnit.Space = ERigVMTransformSpace::LocalSpace;
TransformUnit.Execute(LiveLinkClient, Context);
FTransform BoneTransform = TransformUnit.Transform;
```

### 进阶用法

**结合 LiveLink 输入设备数据**

```cpp
// 来源：LiveLinkControlRig/Source/LiveLinkControlRig/Private/LiveLinkInputDeviceRigUnits.cpp

FRigUnit_LiveLinkEvaluateInputDeviceValue InputUnit;
InputUnit.SubjectName = FName("GamepadSubject");
InputUnit.Execute(); // 内部使用 LiveLinkControlRigUtilities::TryGetLiveLinkClient()

if (InputUnit.InputDeviceData.IsValid())
{
    float LeftStickY = InputUnit.InputDeviceData.LeftAnalogY;
    bool bButtonA = InputUnit.InputDeviceData.ButtonA;
    // 将数据写入 Control Rig 参数
    SetRigElementValue<float>(LeftStickYParam, LeftStickY);
}
```

**自定义节点参数提取**

对于包含自定义参数的 LiveLink 动画帧（例如人脸捕捉的 BlendShape 权重），使用 `FRigUnit_LiveLinkGetParameterValueByName`：

```cpp
FRigUnit_LiveLinkGetParameterValueByName ParamUnit;
ParamUnit.SubjectFrame = SubjectFrameHandle;
ParamUnit.ParameterName = FName("jawOpen");
ParamUnit.Execute();

float JawOpen = ParamUnit.ParameterValue; // 类型取决于具体参数
```

## Demo 示例

以下是一个最小可编译的 C++ Control Rig 模块示例，演示如何在自定义 Control Rig 中使用该插件的节点。假设你的模块已依赖 `LiveLinkControlRig` 和 `ControlRig`。

**MyRig.h**

```cpp
#pragma once
#include "ControlRig.h"
#include "MyRig.generated.h"

UCLASS(BlueprintType)
class UMyRig : public UControlRig
{
    GENERATED_BODY()

public:
    // 此函数在 Control Rig 执行中由 RIGVM 自动调用，无需手动调用 Execute 节点
    // 这里仅为演示如何通过 C++ 访问 LiveLink 数据
    UFUNCTION(BlueprintCallable, Category = "LiveLink")
    void GetLiveLinkBoneTransform(const FName& SubjectName, const FName& BoneName, FTransform& OutTransform);
};
```

**MyRig.cpp**

```cpp
#include "MyRig.h"
#include "LiveLinkRigUnits.h"
#include "LiveLinkClient.h" // 如果使用辅助函数需包含
#include "LiveLinkControlRig.h" // 包含 FLiveLinkControlRigModule 但无需直接使用

void UMyRig::GetLiveLinkBoneTransform(const FName& SubjectName, const FName& BoneName, FTransform& OutTransform)
{
    // 使用 LiveLinkControlRigUtilities::TryGetLiveLinkClient() 获取客户端
    // 注意：该函数位于 LiveLinkRigUnits.h 的命名空间中
    ILiveLinkClient* LiveLinkClient = LiveLinkControlRigUtilities::TryGetLiveLinkClient();
    if (!LiveLinkClient)
    {
        OutTransform = FTransform::Identity;
        return;
    }

    // 构造并执行 Evaluate 节点（需模拟 RIGVM 上下文，此处简化）
    FRigUnit_LiveLinkEvaluteFrameAnimation EvalUnit;
    EvalUnit.SubjectName = SubjectName;
    EvalUnit.bDrawDebug = false;
    // 实际执行时需提供 FRigUnitContext，这里使用假上下文
    // EvalUnit.Execute(Context);

    // 由于缺乏完整上下文，此示例仅为结构展示。真实用法：在 Control Rig 图表中连接节点。
    // 更可靠的方式：在 Control Rig 图表的 EventGraph 中添加这些节点。
    OutTransform = FTransform::Identity;
}
```

**注意**：Rig Unit 的执行依赖 RIGVM 上下文和 `Execute` 函数的正确参数传递。上述代码省略了上下文构造，实际开发中只需在 Control Rig 的 `Construction Event` 或 `Forward Solve` 等事件图中拖拽节点即可，无需手写这些调用。

## 模块依赖

要使用该插件，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心 Control Rig 框架，提供 `FRigUnit`、`RIGVM_METHOD` 等 |
| `LiveLinkInterface` | LiveLink 客户端接口 `ILiveLinkClient` 及类型定义 |
| `LiveLinkAnimationCore` | 动画相关的 LiveLink 结构（如 `FSubjectFrameHandle`、`FLiveLinkAnimationBlueprintStructs`） |
| `LiveLinkInputDevice` | 输入设备角色类型（如 `FLiveLinkGamepadInputDeviceFrameData`） |

**注意**：`LiveLinkInputDevice` 默认并非全局引用，需确保你的项目已启用该插件（`LiveLinkInputDevice` 在 `Engine/Plugins/Runtime/LiveLinkInputDevice`）。

## 维护状态

### 近期更新

- 2025-06-26 ec90099 添加 UE_INLINE_GENERATED_CPP_BY_NAME 到对应的 .gen.cpp 文件
- 2025-04-23 939cc6e 使用 FortniteClient 构建目标查找并转换所有文件以添加 dllstorage
- 2024-01-30 0c7f26b 移动输入设备类型以适应从 Live Link Control Rig 插件访问输入设备数据
- 2023-12-20 f76f124 初始提交：LiveLinkControlRig
- 2023-12-01 3e05871 创建：LiveLink Control Rig

### 维护评价

该插件创建于 2023 年 12 月，至今约 2 年。作为**实验性插件**（`IsBetaVersion=true`），其功能核心稳定，但更新频率较低。最近两次提交（2025 年）仅为编译基础设施变更（添加 dllstorage、内联生成宏），无功能性新增。最后一次功能性更新在 2024 年 1 月（移动输入设备类型）。目前**维护不活跃**，但无废弃提示。由于控制装备和 LiveLink 框架相对稳定，插件仍可正常使用，但建议关注未来可能的功能缺失或与新版 UE 的兼容性。**推荐在新项目中使用**，但需留意潜在的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkControlRig)
- 官方文档：无（`DocsURL` 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkControlRig/Tests)（可能存在，但未提供具体路径）