# Geometry Mask

> 

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质函数、材质、测试纹理） |
| 模块 | `GeometryMask` (Runtime), `GeometryMaskEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/GeometryMask) | |

## 用途

Geometry Mask 是一个基于 Canvas 的 3D 几何遮罩系统，用于将场景中网格体（StaticMesh、DynamicMesh）的轮廓实时渲染为 2D 遮罩纹理。该插件最初为 Virtual Production（尤其是 Motion Design）场景设计，解决的核心问题是：**如何根据 3D 物体的实际几何形状，在运行时生成精确的 2D 遮罩图像**。

与传统基于体积或投影的遮罩方式不同，Geometry Mask 通过将网格体的顶点投影到屏幕空间 Canvas 上，利用 GPU 渲染出精确的几何轮廓。生成的遮罩纹理可供材质、后处理等系统消费，实现物体形状驱动的视觉效果。

**核心特性：**
- **Write/Read 架构**：Writer 组件将网格体形状写入 Canvas，Reader 组件从 Canvas 读取遮罩数据
- **颜色通道复用**：单个 Canvas Resource 纹理可同时容纳最多 3 个不同 Canvas（R/G/B 通道独立分配）
- **后处理效果**：支持高斯模糊（Blur）和边缘羽化（Feather）
- **合成操作**：支持 Add、Subtract、Intersect 三种合成模式
- **Scene View Extension 驱动**：通过 `FGeometryMaskSceneViewExtension` 在渲染管线中自动触发 Canvas 更新

## 使用场景

- 你在做虚拟制片中的 Motion Design，需要根据 3D 元素的形状生成遮罩来控制材质混合 → 用 Geometry Mask
- 你需要根据场景中物体的屏幕空间轮廓来应用后处理效果（如光晕、描边）→ 用 Geometry Mask 生成遮罩纹理，再在材质中采样
- 你需要将多个 3D 形状的遮罩打包到一张纹理的不同通道中以提高性能 → Geometry Mask 的颜色通道分配机制自动处理

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTexture` | 获取 Canvas 的渲染目标纹理 | `AGeometryMaskCanvasActor` |
| `GetTexture` | 获取 Canvas 的渲染目标纹理 | `UGeometryMaskCanvasReferenceComponentBase` |
| `GetTexture` | 获取 Canvas 底层 RenderTarget | `UGeometryMaskCanvas` |
| `GetColorChannel` | 获取当前 Canvas 使用的颜色通道 | `UGeometryMaskCanvas` |
| `ReceiveSetCanvas` (BlueprintImplementableEvent) | Canvas 关联时的蓝图回调 | `UGeometryMaskCanvasReferenceComponentBase` |
| `GetDefaultCanvas` | 获取默认空白 Canvas | `UGeometryMaskSubsystem` |

### 使用示例（蓝图描述）

**设置 Writer（写入遮罩）：**

1. 在场景中放置一个带有 StaticMesh 的 Actor
2. 添加 `UGeometryMaskWriteMeshComponent` 组件
3. 设置 `Parameters.CanvasName` 为一个自定义名称（如 `"MyMask"`）
4. 设置 `Parameters.ColorChannel`（如 Red）
5. 设置 `Parameters.OperationType`（Add/Subtract/Intersect）
6. 可选：调整 `Parameters.OuterRadius` / `InnerRadius` 控制遮罩形状的缩放偏移

**设置 Reader（读取遮罩）：**

1. 在需要消费遮罩的 Actor 上添加 `UGeometryMaskReadComponent` 组件
2. 设置 `Parameters.CanvasName` 为与 Writer 相同的名称
3. 设置 `Parameters.ColorChannel` 为与 Writer 对应的通道
4. 在蓝图中实现 `ReceiveSetCanvas` 事件，通过 `GetTexture()` 获取遮罩纹理
5. 将纹理传递给材质参数进行采样

**使用 CanvasActor：**

1. 放置 `AGeometryMaskCanvasActor` 到场景
2. 设置 `CanvasName`
3. 该 Actor 会自动发现子 Actor 上的 Writer 并注册

## C++ 用法

### 头文件引入

```cpp
#include "GeometryMaskCanvas.h"
#include "GeometryMaskWriteComponent.h"
#include "GeometryMaskReadComponent.h"
#include "GeometryMaskSubsystem.h"
#include "GeometryMaskWorldSubsystem.h"
#include "GeometryMaskTypes.h"
```

### 基本用法

**获取 Canvas（通过 WorldSubsystem）：**

```cpp
// 来源: GeometryMaskWorldSubsystem.h
UGeometryMaskWorldSubsystem* WorldSubsystem = GetWorld()->GetSubsystem<UGeometryMaskWorldSubsystem>();
UGeometryMaskCanvas* Canvas = WorldSubsystem->GetNamedCanvas(Level, FName("MyCanvas"));

// 获取该 Level 下所有 Canvas 名称
TArray<FName> CanvasNames = WorldSubsystem->GetCanvasNames(Level);
```

**获取默认 Canvas（通过 EngineSubsystem）：**

```cpp
// 来源: GeometryMaskSubsystem.h
UGeometryMaskSubsystem* Subsystem = GEngine->GetEngineSubsystem<UGeometryMaskSubsystem>();
UGeometryMaskCanvas* DefaultCanvas = Subsystem->GetDefaultCanvas();
```

**配置 Canvas 模糊和羽化：**

```cpp
// 来源: GeometryMaskCanvas.h
Canvas->SetApplyBlur(true);
Canvas->SetBlurStrength(16.0);

Canvas->SetApplyFeather(true);
Canvas->SetOuterFeatherRadius(16);
Canvas->SetInnerFeatherRadius(16);
```

**监听 Canvas 资源创建/销毁：**

```cpp
// 来源: GeometryMaskSubsystem.h
UGeometryMaskSubsystem* Subsystem = GEngine->GetEngineSubsystem<UGeometryMaskSubsystem>();
Subsystem->OnGeometryMaskResourceCreated().AddLambda([](const UGeometryMaskCanvasResource* Resource) {
    // 新的 GPU 资源已创建
});
```

### 进阶用法

**自定义 Writer（实现 IGeometryMaskWriteInterface）：**

```cpp
// 来源: IGeometryMaskWriteInterface.h
class UMyCustomWriter : public UActorComponent, public IGeometryMaskWriteInterface
{
    // 必须实现的接口方法:
    virtual const FGeometryMaskWriteParameters& GetParameters() const override;
    virtual void SetParameters(FGeometryMaskWriteParameters& InParameters) override;
    virtual void DrawToCanvas(FCanvas* InCanvas) override;  // 核心：向 Canvas 绘制形状
    virtual FOnGeometryMaskSetCanvasNativeDelegate& OnSetCanvas() override;
};
```

**自定义 Reader（实现 IGeometryMaskReadInterface）：**

```cpp
// 来源: IGeometryMaskReadInterface.h
class UMyCustomReader : public UActorComponent, public IGeometryMaskReadInterface
{
    virtual const FGeometryMaskReadParameters& GetParameters() const override;
    virtual void SetParameters(FGeometryMaskReadParameters& InParameters) override;
    virtual FOnGeometryMaskSetCanvasNativeDelegate& OnSetCanvas() override;
};
```

**监听 Canvas 激活/停用：**

```cpp
// 来源: GeometryMaskCanvas.h
Canvas->OnActivated().AddLambda([]() {
    // Writers 列表变为非空
});
Canvas->OnDeactivated().AddLambda([]() {
    // Writers 列表变为空
});
```

## 架构概览

```
UGeometryMaskSubsystem (EngineSubsystem, 单例)
├── CanvasResources 池 (GPU 纹理资源)
├── DefaultCanvas
└── Update() → 遍历所有 World

UGeometryMaskWorldSubsystem (每个 World 一个)
├── LevelStates: Map<ULevel, FGeometryMaskLevelState>
│   └── NamedCanvases: Map<FName, UGeometryMaskCanvas>
├── FGeometryMaskSceneViewExtension (渲染钩子)
│   └── BeginRenderViewFamily → 触发 Canvas 更新
└── GetNamedCanvas() / GetCanvasNames()

UGeometryMaskCanvas (逻辑 Canvas)
├── CanvasName / CanvasId
├── Writers: TArray<IGeometryMaskWriteInterface>
├── 模糊/羽化参数
├── ColorChannel (分配的 R/G/B 通道)
└── CanvasResource → UGeometryMaskCanvasResource

UGeometryMaskCanvasResource (GPU 资源)
├── RenderTargetTexture (UCanvasRenderTarget2D)
├── DependentCanvasIds: Map<Channel, CanvasId>
├── PostProcess_Blur / PostProcess_DistanceField
└── Checkout/Checkin 通道分配

Writer 组件: UGeometryMaskWriteMeshComponent
├── 缓存 StaticMesh / DynamicMesh 的顶点数据
├── DrawToCanvas() → BatchedElements 三角形绘制
└── 支持 Add/Subtract/Intersect 操作

Reader 组件: UGeometryMaskReadComponent
├── 关联 Canvas，获取 ColorChannel
└── GetTexture() → 消费遮罩纹理
```

## 内容资产

插件包含以下材质/纹理资产（`Content/GeometryMask/`）：

| 资产 | 类型 | 说明 |
|---|---|---|
| `MF_ApplyGeometryMask` | Material Function | 应用 Geometry Mask 的通用材质函数 |
| `MF_ApplyMask2D` | Material Function | 2D 遮罩应用（双通道） |
| `MF_ApplyMask2D_Single` | Material Function | 2D 遮罩应用（单通道） |
| `MF_ApplyMaskFeather` | Material Function | 羽化效果材质函数 |
| `M_GeometryMaskPreview` | Material | 遮罩预览材质 |
| `M_GeometryMaskUsageExample` | Material | 使用示例材质 |
| `T_GeometryMaskTestTexture` | Texture | 测试纹理 |

## Shader

插件包含两个 Compute Shader（`Shaders/Private/`）：

| Shader | 说明 |
|---|---|
| `GeometryMaskBlurCS.usf` | 高斯模糊后处理 Compute Shader |
| `GeometryMaskJFInitCS.usf` | Jump Flooding 算法初始化（用于距离场/羽化） |
| `GeometryMaskJFStepCS.usf` | Jump Flooding 算法迭代步进 |

## 模块依赖

### GeometryMask (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、Component 等） |
| `DeveloperSettings` | 配置系统（私有） |
| `GeometryCore` | 几何核心库（私有） |
| `GeometryFramework` | DynamicMesh 支持（私有） |
| `RHI` | 渲染硬件接口（私有） |
| `RenderCore` | 渲染核心（私有） |
| `Renderer` | 渲染器（私有） |

### GeometryMaskEditor (Editor)

| 模块 | 用途 |
|---|---|
| `CoreUObject` | UObject 系统 |
| `GeometryMask` | 运行时模块 |
| `SlateCore` | UI 框架核心 |
| `Slate` | UI 框架（私有） |
| `UnrealEd` | 编辑器功能（私有） |
| `InputCore` | 输入系统（私有） |
| `WorkspaceMenuStructure` | 编辑器面板结构（私有） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `df329aa` | Motion Design: removed beta tag from motion design plugins | 插件正式脱离 beta 状态，标志着功能稳定 |
| 2025-09-12 | `ce6ff39` | Addressing `nodiscard` attribute issues for FTSTicker::RemoveTicker | 编译警告修复，无功能变更 |
| 2025-09-03 | `88ab9d9` | Add ability to write the same mesh multiple times if used in multiple components under the actor | 功能增强：同一 Actor 下多个组件可共享同一网格数据写入遮罩 |

### 维护评价

- **创建时间**：2024 年 1 月（从 Experimental 迁移到 VirtualProduction）
- **最近更新**：2025 年 9 月，有实质性功能更新
- **活跃程度**：**活跃维护**，近 6 个月内有功能增强
- **已知限制**：
  - 每个 Canvas Resource 最多使用 3 个颜色通道（R/G/B，不使用 Alpha，因为 RT 格式对 Alpha 支持不一致）
  - 最大纹理尺寸 8192
  - 网格缓存基于组件数量变化触发，不检测网格顶点数据变化（StaticMesh）；DynamicMesh 通过 ChangeStamp 机制检测
- **推荐程度**：✅ 推荐使用，特别是 Motion Design / Virtual Production 场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/GeometryMask)
