# Render Trace

> The Render Trace plugin provides a way to have pixel perfect sampling of physical materials on meshes.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 需手动启用 |
| 包含内容 | 无 |
| 模块 | RenderTrace (Runtime) |
| 创建时间 | 2022-06-30 |
| 年龄标签 | 🆕 (~4年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RenderTrace) | |

## 用途

Render Trace 解决的核心问题是：**在 GPU 上以像素级精度确定网格表面的物理材质（Physical Material）**。

传统做法中，物理材质通常按材质槽（Material Slot）绑定——整个材质槽共享一个物理材质。但如果你的材质在材质图中混合了多种表面（比如一个地形材质同时包含草地、泥土、岩石），你无法通过简单射线检测得知射线命中了哪种表面。

Render Trace 通过自定义渲染通道（Custom Mesh Pass）解决这个问题：它将每个物理材质的权重编码到一个特殊 shader 中，然后用 GPU Readback 异步读取结果。整个过程不阻塞游戏线程或渲染线程。

**注意**: 此插件处于 **Beta** 状态（`IsBetaVersion: true`），且默认禁用。

## 使用场景

- 你在做射击游戏，子弹击中地面时需要根据实际表面播放不同音效/粒子效果（草地 vs 泥土 vs 金属），而这些表面混合在同一个材质图中
- 你在做角色脚步声系统，地形材质混合了多种物理材质，需要精确知道脚踩在哪个区域
- 你需要在运行时对网格的特定像素位置进行物理材质采样，而不是粗粒度的材质槽匹配

## 蓝图用法

此插件**没有暴露蓝图节点**。`FRenderTraceQueue` 是纯 C++ 类，不继承 `UObject`，也没有 `UFUNCTION(BlueprintCallable)` 标记。所有调用都必须在 C++ 中完成。

## C++ 用法

### 启用插件

1. 在 `.uproject` 或编辑器插件设置中启用 `RenderTrace` 插件
2. 运行时需要通过控制台变量启用渲染追踪：

```cpp
// 控制台变量
RenderTrace.Enabled 1
```

### 头文件引入

```cpp
#include "RenderTrace.h"
```

### 核心 API

插件的核心类是 `FRenderTraceQueue`，它管理异步 GPU 渲染任务的生命周期：

```cpp
// 定义结果回调委托
FRenderTraceDelegate MyCallback;
MyCallback.BindLambda([](uint32 TaskID, const UPhysicalMaterial* PhysicalMaterial, int64 UserData)
{
    if (PhysicalMaterial)
    {
        UE_LOG(LogTemp, Log, TEXT("Hit physical material: %s"), *PhysicalMaterial->GetName());
    }
});

// 创建队列实例（通常作为成员变量持有）
FRenderTraceQueue RenderTraceQueue;

// 提交异步渲染任务
// - PrimitiveComponents: 要检测的组件列表（材质中必须配置了 Physical Material Output 节点）
// - RayOrigin: 射线起点（世界空间）
// - RayDirection: 射线方向
// - OnComplete: 完成回调（在游戏线程触发）
// - UserData: 自定义数据（透传到回调）
// - 返回值: TaskID（0 表示失败）
uint32 TaskID = RenderTraceQueue.AsyncRenderTraceComponents(
    PrimitiveComponents,
    RayOrigin,
    RayDirection,
    MyCallback,
    0 /* UserData */
);

// 可选：取消任务
RenderTraceQueue.CancelAsyncSample(TaskID);

// 检查是否已启用
if (FRenderTraceQueue::IsEnabled())
{
    // ...
}
```

### 材质端配置

在材质编辑器中使用 **Physical Material Output** 节点（位于 "Render Trace" 分类下）：

1. 在材质图中添加 `Physical Material Output` 节点
2. 为每个输入配置一个 `UPhysicalMaterial` 资产
3. 将权重值（0~1 的 float）连接到每个输入——表示该像素属于该物理材质的概率
4. Shader 会选择权重最高的物理材质作为结果

**限制**: 每个材质最多支持 **16 个**物理材质输入。

### 模块依赖

如需在自己的 Build.cs 中依赖此插件：

```csharp
PrivateDependencyModuleNames.Add("RenderTrace");
```

注意：RenderTrace 模块自身的依赖全部为 Private，因此你的模块只需直接依赖 `RenderTrace` 即可，无需额外引用其内部依赖。

## Demo 示例

### 最小可运行示例

```cpp
// MyComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "RenderTrace.h"
#include "MyComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

private:
    FRenderTraceQueue RenderTraceQueue;
    uint32 PendingTaskID = 0;

    void OnTraceComplete(uint32 TaskID, const UPhysicalMaterial* PhysicalMaterial, int64 UserData);
};
```

```cpp
// MyComponent.cpp
#include "MyComponent.h"
#include "Components/PrimitiveComponent.h"

void UMyComponent::BeginPlay()
{
    Super::BeginPlay();
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (PendingTaskID == 0 && FRenderTraceQueue::IsEnabled())
    {
        // 获取目标组件（比如一个地面网格）
        TArray<const UPrimitiveComponent*> Components;
        if (UPrimitiveComponent* Ground = /* 你的目标组件 */)
        {
            Components.Add(Ground);
        }

        if (!Components.IsEmpty())
        {
            FVector Origin = GetOwner()->GetActorLocation();
            FVector Direction = FVector::DownVector;

            FRenderTraceDelegate Callback;
            Callback.BindUObject(this, &UMyComponent::OnTraceComplete);

            PendingTaskID = RenderTraceQueue.AsyncRenderTraceComponents(
                Components, Origin, Direction, Callback);
        }
    }
}

void UMyComponent::OnTraceComplete(uint32 TaskID, const UPhysicalMaterial* PhysicalMaterial, int64 UserData)
{
    PendingTaskID = 0;
    if (PhysicalMaterial)
    {
        UE_LOG(LogTemp, Log, TEXT("Surface material: %s"), *PhysicalMaterial->GetName());
        // 根据物理材质播放对应的音效/粒子等
    }
}
```

### Build.cs

```csharp
using UnrealBuildTool;

public class MyModule : ModuleRules
{
    public MyModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.Add("RenderTrace");
    }
}
```

## 模块依赖

以下为 RenderTrace 模块的 **Private** 依赖（使用者无需关心，仅供了解内部结构）：

| 模块 | 用途 |
|---|---|
| `ApplicationCore` | 应用层核心功能 |
| `Core` | 基础库 |
| `CoreUObject` | UObject 系统 |
| `DeveloperSettings` | 开发者设置 |
| `Engine` | 引擎核心 |
| `Projects` | 插件项目管理 |
| `RHI` | 渲染硬件接口（GPU Readback） |
| `RenderCore` | 渲染核心 |
| `Renderer` | 渲染器（Mesh Pass Processor） |
| `EditorFramework` | 编辑器框架（仅编辑器） |
| `MaterialUtilities` | 材质工具（仅编辑器） |
| `Slate` / `SlateCore` | UI 框架（仅编辑器） |
| `UnrealEd` | 编辑器（仅编辑器） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-04-23 | `fcd8083c3944` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticvar instead of on types. | 编译适配改动，将 DLL 导出标记从类型改为方法/静态变量，不影响功能 |
| 2025-03-20 | `80c69d990a58` | Updated bit-width of material value types to 64-bits | 材质值类型位宽更新到 64 位，可能影响 shader 中的数据精度 |
| 2025-02-13 | `8b1c9518c431` | First Person: Decoupled applying the first person transform from evaluating WPO... | 第一人称渲染与 WPO 解耦，RenderTrace shader 中的 `ApplyMaterialFirstPersonTransform` 调用随之调整 |

### 维护评价

- **创建时间**: 2022 年 6 月，约 4 年历史
- **Beta 状态**: 插件始终标记为 `IsBetaVersion: true`，表明 Epic 将其视为实验性功能
- **默认禁用**: `EnabledByDefault: false`，需要用户手动启用
- **维护状态**: 活跃——2025 年仍有实质性更新（材质值类型精度变更、第一人称渲染解耦）
- **已知限制**:
  - 每个材质最多 16 个物理材质输入
  - 仅支持 SM5 及以上特性级别（`ERHIFeatureLevel::SM5`）
  - 仅处理 LOD 0 的第一个 MeshElement
  - 无蓝图接口，纯 C++ API
- **推荐度**: 如果你的游戏需要像素级物理材质采样，且材质中混合了多种物理材质表面，这个插件是唯一解决方案。但因为是 Beta 状态，生产环境使用需谨慎测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RenderTrace)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：未发现独立测试文件
