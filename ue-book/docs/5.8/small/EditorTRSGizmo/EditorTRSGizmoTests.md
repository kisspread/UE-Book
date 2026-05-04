# Editor TRS Gizmo

> A temporary plugin for New TRS Gizmo work（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `EditorTRSGizmoTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTRSGizmo) | |

## 用途

这是一个用于 UE5.8 新版 TRS（Translate/Rotate/Scale）变换 Gizmo 开发和测试的实验性插件。它不是面向最终用户的功能插件，而是 Epic 内部用于验证新 Gizmo 行为正确性的自动化测试框架。

该插件解决的核心问题是：**如何系统化地测试 3D 视口中变换 Gizmo 的各种交互模式**。它提供了：

1. **测试世界管理**：自动创建/销毁编辑器世界，管理 Actor 的生成、选择、状态捕获与恢复
2. **Gizmo 交互模拟**：通过自动化驱动（Automation Driver）模拟鼠标拖拽，测试 Gizmo 在不同坐标系、不同轴向、不同交互类型（直接/间接）下的变换结果
3. **OBS 录制集成**：通过 WebSocket 连接 OBS Studio，自动录制测试过程的视频，便于人工审查失败用例
4. **变换结果验证**：提供工具函数计算平移增量、旋转增量、缩放增量，用于断言 Gizmo 行为是否符合预期

## 使用场景

- 你正在开发或修改 UE 的 Transform Gizmo → 用此插件运行回归测试
- 你需要验证 Gizmo 在不同坐标系（世界/本地）、不同组件类型（轴向/平面/均匀/屏幕/Arcball）下的行为
- 你需要录制 Gizmo 交互的自动化测试视频用于 bug 报告或代码审查

## 蓝图用法

此插件为纯 C++ 测试模块，不包含蓝图可调用的 API。所有功能通过 C++ 自动化测试框架使用。

## C++ 用法

### 头文件引入

```cpp
#include "InteractiveToolsFrameworkTestUtilities.h"
#include "TransformGizmoTestUtilities.h"
```

### 基本用法 — 测试世界管理

`FTestWorld` 是测试基础设施的核心类，负责管理编辑器世界和 Actor 生命周期。

```cpp
// 来源: Private/Tests/InteractiveToolsFrameworkTestUtilities.h

using namespace UE::Editor::InteractiveToolsFramework::Tests;

// 创建测试世界
TSharedRef<FEditorProvider> EditorProvider = MakeShared<FEditorProvider>();
FTestWorld TestWorld;
TestWorld.Initialize(EditorProvider);

// 生成 Actor
FTransform SpawnTransform(FVector(100, 200, 0));
AStaticMeshActor* Cube = TestWorld.SpawnCube(TEXT("TestCube"), SpawnTransform);

// 选择 Actor（触发 Gizmo 显示）
TestWorld.SelectActor(Cube);

// 捕获状态，后续可恢复
TestWorld.CaptureState();

// ... 执行 Gizmo 交互测试 ...

// 恢复到之前的状态
TestWorld.RestoreState();

// 设置视口相机位置
TestWorld.SetViewportCamera(FVector(0, 0, 500), FRotator(-90, 0, 0));

// 清理
TestWorld.Reset();
```

### 基本用法 — 变换 Gizmo 测试

`TTransformGizmoTest` 是 Gizmo 测试的基类模板，提供 Gizmo 交互的核心方法。

```cpp
// 来源: Private/Tests/TransformGizmoTestUtilities.h

using namespace UE::Editor::InteractiveToolsFramework::TransformGizmoTests;

// 获取指定 Gizmo 部件的命中位置
FVector HitPosition;
bool bHit = GetHitPositionForPart(ETransformGizmoPartIdentifier::TranslateXAxis, HitPosition);

// 设置变换模式（通过快捷键模拟用户输入）
SetTransformMode(EGizmoTransformMode::Translate);

// 设置坐标系
SetCoordinateSystem(ECoordSystem::COORD_World);
```

### 进阶用法 — 构建 Gizmo 交互测试参数

```cpp
// 来源: Private/Tests/TransformGizmoTestUtilities.h

// 获取特定变换模式支持的组件类型
TArray<EGizmoComponentType> ComponentTypes = 
    GetGizmoComponentTypesForTransformMode(EGizmoTransformMode::Rotate);
// 返回: Axis, Planar, Uniform, Screen, Arcball

// 获取特定组件类型和变换模式下的有效轴向组合
TArray<EAxisList::Type> AxisLists = 
    GetAxisListValuesForTransformModeAndComponentType(
        EGizmoTransformMode::Translate, EGizmoComponentType::Axis);
// 返回: X, Y, Z, XY, XZ, YZ, XYZ 等

// 构造测试参数
FInteractionTestParams Params;
Params.PartId = ETransformGizmoPartIdentifier::TranslateXAxis;
Params.TransformMode = EGizmoTransformMode::Translate;
Params.InteractionType = EInteractionType::Direct;
Params.ComponentType = EGizmoComponentType::Axis;
Params.CoordinateSystem = ECoordSystem::COORD_World;
Params.AxisList = EAxisList::X;
Params.ViewportType = EViewportType::Perspective;
```

### 进阶用法 — 变换增量计算

```cpp
// 来源: Private/Tests/TransformGizmoTestUtilities.h

FTransform PreviousTransform(FVector(0, 0, 0));
FTransform NewTransform(FVector(100, 0, 0));

// 计算沿 X 轴的平移增量
float TranslateDelta = GetTranslateDeltaAlongAxis(PreviousTransform, NewTransform, EAxis::X);
// 结果: 100.0

// 计算绕 Z 轴的旋转增量
float RotateDelta = GetRotateDeltaOnAxis(PreviousTransform, NewTransform, EAxis::Z);

// 计算沿 Y 轴的缩放增量
float ScaleDelta = GetScaleDeltaAlongAxis(PreviousTransform, NewTransform, EAxis::Y);
```

### 进阶用法 — OBS 录制集成

```cpp
// 来源: Private/Tests/OBSClient.h

using namespace OBS;

// 创建 OBS 客户端并连接
TSharedRef<FOBSClient> OBSClient = MakeShared<FOBSClient>();
TFuture<bool> ConnectFuture = OBSClient->Connect();
// 等待连接完成...

// 开始录制测试过程
OBSClient->StartRecord();

// ... 执行 Gizmo 测试 ...

// 停止录制
OBSClient->StopRecord();

// 管理 OBS 场景
TFuture<TValueOrError<FGetSceneListResponse, void>> SceneListFuture = OBSClient->GetSceneList();
```

## Demo 示例

以下是一个完整的 Gizmo 测试用例示例：

```cpp
// TransformGizmoTranslateTest.h
#pragma once

#include "Misc/AutomationTest.h"
#include "TransformGizmoTestUtilities.h"

class FTransformGizmoTranslateAxisTest
    : public UE::Editor::InteractiveToolsFramework::TransformGizmoTests::TTransformGizmoTest<
        FTransformGizmoTranslateAxisTest, FAutomationTestBase>
{
public:
    void RunTest()
    {
        // 1. 初始化测试世界
        Setup();
        
        // 2. 生成并选择 Actor
        FTransform SpawnTransform(FVector(0, 0, 0));
        AStaticMeshActor* Cube = TestWorld.SpawnCube(TEXT("TestCube"), SpawnTransform);
        TestWorld.SelectActor(Cube);
        TestWorld.CaptureState();
        
        // 3. 设置为平移模式 + 世界坐标系
        SetTransformMode(EGizmoTransformMode::Translate);
        SetCoordinateSystem(ECoordSystem::COORD_World);
        
        // 4. 获取 X 轴 Gizmo 部件的命中位置
        FVector HitPosition;
        GetHitPositionForPart(ETransformGizmoPartIdentifier::TranslateXAxis, HitPosition);
        
        // 5. 沿 X 轴方向拖拽
        FTransform PreviousTransform = Cube->GetActorTransform();
        
        TestTransformDirectAxis(
            {},  // 无修饰键
            {EMouseButtons::Left},
            ETransformGizmoPartIdentifier::TranslateXAxis,
            EAxis::X,
            FVector2D(1, 0),  // 向右拖拽
            GetTranslateDeltaAlongAxis,
            [](const FTransform& T, EAxis::Type A) -> FString {
                return FString::Printf(TEXT("X=%f"), T.GetLocation().X);
            },
            TEXT("translated")
        );
        
        // 6. 验证变换结果
        FTransform NewTransform = Cube->GetActorTransform();
        float Delta = GetTranslateDeltaAlongAxis(PreviousTransform, NewTransform, EAxis::X);
        // TestEqual("Actor should have moved along X", Delta, ExpectedDelta);
        
        // 7. 清理
        TestWorld.RestoreState();
        TestWorld.Reset();
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 交互式工具框架，Gizmo 的基础架构 |
| `EditorGizmos` | 编辑器 Gizmo 实现（TransformGizmo 等） |
| `AutomationDriver` | 自动化驱动，模拟用户输入（鼠标/键盘） |
| `CQTest` | C++ 查询式测试框架 |
| `OBSClient`（内部模块） | OBS WebSocket 客户端，用于录制测试视频 |
| `TypedElementFramework` | 类型化元素框架，用于选择集管理 |

## 维护状态

### 近期更新

由于该插件创建时间为 2026-03-19（属于 UE 5.8 开发周期），git log 信息暂不可用。根据 .uplugin 元数据：

- 插件标记为 `IsExperimentalVersion: true`
- 标记为"临时插件"（temporary plugin）
- 仅包含测试模块，无运行时功能

### 维护评价

⚠️ **实验性临时插件 — 请谨慎使用**

- **性质**：这是一个 Epic 内部用于开发新版 Transform Gizmo 的测试插件，不是面向公众的功能插件
- **稳定性**：标记为实验性（IsExperimentalVersion=true），API 和行为可能随时变更
- **生命周期**：作为"临时"插件，一旦新版 Gizmo 开发完成并集成到引擎核心，此插件可能会被移除
- **适用范围**：仅适用于需要参与 Gizmo 开发或扩展 Gizmo 测试的开发者
- **不推荐**用于生产项目或作为外部依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTRSGizmo)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTRSGizmo/Source/EditorTRSGizmoTests/Private/Tests)