# Actor Layer Utilities

> Utilites for interacting with actor layers from blueprints

| 属性 | 值 |
|---|---|
| 分类 | Runtime |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | ActorLayerUtilities (Runtime), ActorLayerUtilitiesEditor (Editor) |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ActorLayerUtilities) | |

## 用途

ActorLayerUtilities 提供了一套蓝图函数库（`ULayersBlueprintLibrary`），让你能在**运行时**和**蓝图**中操作 Unreal 的 Actor Layer（编辑器图层）系统。

Unreal 的 Layer 系统原本是纯编辑器功能——在 World Outliner 的 Layers 面板中创建图层，将 Actor 拖入不同图层来组织场景。但这个 plugin 打开了一个缺口：它把图层的查询和操作暴露给了蓝图和运行时代码。

核心价值：**用图层名称作为标签（Tag），在运行时按组批量获取和管理 Actor**。这比在每个 Actor 上手动设置 Tag 或 Group 更方便，因为图层在编辑器中已有完善的 UI 支持。

## 使用场景

- 你需要在运行时获取"所有灯光层的 Actor"来统一控制开关 → 用 `GetActors` 配合指定 Layer
- 你在编辑器中已经用 Layers 面板把场景组织好了（环境层、敌人层、道具层），现在想在蓝图中按层操作 → 用这个 plugin 直接按 Layer Name 查询
- 你需要在运行时动态将 Actor 加入/移除某个逻辑分组 → 用 `AddActorToLayer` / `RemoveActorFromLayer`
- 你在做关卡流送或多场景管理，需要按层批量 show/hide Actor → 先按层获取 Actor，再统一操作

## 蓝图用法

### 核心数据结构

**FActorLayer** — 一个简单的结构体，只有一个 `Name`（FName）属性，用来指定目标图层名称。

在蓝图中使用时，Details 面板会显示一个自定义的下拉选择器（由 Editor 模块提供），支持：
- 从下拉菜单选择已有图层
- 从 Layers 面板拖拽图层过来
- 点击按钮快速选中该图层中的所有 Actor

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetActors` | 获取指定图层中的所有 Actor，返回 `TArray<AActor*>` | `ULayersBlueprintLibrary` |
| `AddActorToLayer` | 将 Actor 添加到指定图层（如果已在则不重复） | `ULayersBlueprintLibrary` |
| `RemoveActorFromLayer` | 将 Actor 从指定图层中移除 | `ULayersBlueprintLibrary` |

### 使用示例（蓝图描述）

**场景 1：获取图层中的所有 Actor**

1. 在蓝图中拖出一个 `GetActors` 节点
2. `WorldContextObject` 连接 Self（或当前 World Context）
3. `ActorLayer` 参数设置为目标图层名（如 "Lights"、"Enemies"）
4. 输出是一个 Actor 数组，可以用 ForEach 循环处理

**场景 2：运行时动态分组**

1. 当某个 Actor 生成后，拖出 `AddActorToLayer` 节点
2. 连接该 Actor 引用
3. `Layer` 参数设为目标图层名（如 "ActiveEnemies"）
4. 之后就可以用 `GetActors("ActiveEnemies")` 批量获取

## C++ 用法

### 头文件引入

```cpp
#include "ActorLayerUtilities.h"
```

### 基本用法

```cpp
// 获取指定图层中的所有 Actor
FActorLayer Layer;
Layer.Name = FName("MyLayer");
TArray<AActor*> Actors = ULayersBlueprintLibrary::GetActors(this, Layer);

// 将 Actor 添加到图层
ULayersBlueprintLibrary::AddActorToLayer(MyActor, Layer);

// 将 Actor 从图层移除
ULayersBlueprintLibrary::RemoveActorFromLayer(MyActor, Layer);
```

### 进阶用法

```cpp
// 遍历多个图层，收集所有相关 Actor
TArray<FName> LayerNames = { FName("Lights"), FName("FX") };
TArray<AActor*> AllActors;

for (const FName& LayerName : LayerNames)
{
    FActorLayer Layer;
    Layer.Name = LayerName;
    AllActors.Append(ULayersBlueprintLibrary::GetActors(this, Layer));
}

// 运行时切换 Actor 的图层归属
FActorLayer OldLayer;
OldLayer.Name = FName("Inactive");
FActorLayer NewLayer;
NewLayer.Name = FName("Active");

ULayersBlueprintLibrary::RemoveActorFromLayer(MyActor, OldLayer);
ULayersBlueprintLibrary::AddActorToLayer(MyActor, NewLayer);
```

**注意**：`GetActors` 的实现是遍历 World 中的所有 Actor 并检查 `Actor->Layers` 数组是否包含目标 Layer Name。在 Actor 数量很大的场景中，这可能有性能开销。

## Demo 示例

### Build.cs 依赖

```csharp
// 你的模块 Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "ActorLayerUtilities"
});
```

### 完整示例：按图层控制灯光

```cpp
// LayerLightController.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LayerLightController.generated.h"

UCLASS()
class ALayerLightController : public AActor
{
    GENERATED_BODY()

public:
    // 要控制的灯光图层名称
    UPROPERTY(EditAnywhere, Category = "Layer")
    FName LightLayerName = FName("Lights");

    // 切换灯光开关
    UFUNCTION(BlueprintCallable, Category = "Layer")
    void ToggleLights();

private:
    bool bLightsOn = true;
};
```

```cpp
// LayerLightController.cpp
#include "LayerLightController.h"
#include "ActorLayerUtilities.h"
#include "Components/LightComponent.h"

void ALayerLightController::ToggleLights()
{
    FActorLayer Layer;
    Layer.Name = LightLayerName;

    TArray<AActor*> LightActors = ULayersBlueprintLibrary::GetActors(this, Layer);

    bLightsOn = !bLightsOn;

    for (AActor* Actor : LightActors)
    {
        TArray<ULightComponent*> Lights;
        Actor->GetComponents<ULightComponent>(Lights);
        for (ULightComponent* Light : Lights)
        {
            Light->SetVisibility(bLightsOn);
        }
    }
}
```

## 模块依赖

如果你要使用 ActorLayerUtilities，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ActorLayerUtilities` | 提供 `ULayersBlueprintLibrary` 和 `FActorLayer` |
| `Core` | 基础类型（FName 等） |
| `CoreUObject` | UObject 系统 |

ActorLayerUtilities 自身的内部依赖：

| 模块 | 用途 |
|---|---|
| `Engine` | World 遍历、Actor 系统（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-05-15 | `da92084a` | Optimized out more private modules includes and dependencies | 清理私有模块依赖，属于构建优化 |
| 2023-01-13 | `3c9aacb1` | Updated public headers using IWYU (~170 plugins) | 批量 IWYU 改进，非功能性变更 |
| 2023-01-12 | `2f78497e` | Updated private files with IWYU for all plugins | 同上，IWYU 清理 |

### 维护评价

- **创建时间**：2020-10-22，约 5.5 年前
- **最近更新**：最后一次实质性更新在 2023 年 5 月，且仅是编译依赖清理，非功能变更
- **代码规模**：极小——运行时模块仅约 50 行有效代码，3 个函数
- **维护状态**：**维护不活跃** — 自 2023 年以来无任何更新（超过 2 年无 commit）
- **已知限制**：
  - `GetActors` 通过遍历全部 Actor 实现，无索引/缓存，大数据量场景性能较差
  - 只有 3 个函数，功能非常有限
  - 没有官方测试用例
- **推荐使用**：✅ 可以使用。代码简单稳定，不太可能出 bug。但如果你需要高性能的按标签查询，考虑自己维护一个 `TMap<FName, TArray<AActor*>>` 索引。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ActorLayerUtilities)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：无
