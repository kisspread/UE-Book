# Water

> Full suite of water tools and rendering techniques to easily add oceans, river, lakes or custom water bodies that carve landscape and interacts with gameplay

| 属性 | 值 |
|---|---|
| 中文名 | 水体工具 |
| 分类 | Water |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、网格体、纹理） |
| 模块 | `Water` (Runtime), `WaterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Water) | |

## 用途

Water 插件是 UE5 中实现完整水体系统的编辑器工具集。它允许你在关卡中快速添加海洋、河流、湖泊或自定义水体，并自动雕刻地形、生成水花、模拟波浪以及与游戏玩法交互。该插件解决的核心问题是：传统水体实现需要复杂的材质和蓝图编写，而 Water 通过可见的编辑器画笔、自动化的地形修改、波浪编辑器和运行时信息纹理，将水体系统集成到标准地形工作流中。

**核心机制**：  
- 使用 `AWaterLandscapeBrush`（继承自 `ALandscapeBlueprintBrush`）作为地形画笔，在编辑模式下实时雕刻河床、海岸线。  
- 通过 `UJumpFloodComponent2D` 快速生成水体距离场，用于冲刷和与地形交互。  
- 提供专用的波浪编辑器（`FWaterWavesEditorToolkit`）编辑频谱形状和水面动画。  
- 自动管理 `WaterInfoTexture`（运行时水面高度、速度、深度信息），供 Niagara 粒子、材质等使用。

## 使用场景

- 你正在制作一个开放世界游戏，需要大规模海洋、河流系统，且地形会根据水体自动形变。  
- 你需要通过编辑器直观地绘制河流路径并即时看到地形被雕刻的效果。  
- 你想要编辑波浪频谱来模拟不同天气条件下的水面动画（平静湖泊 -> 风暴海洋）。  
- 项目需要运行时水面与游戏玩法交互（如物理浮力、水流速度影响角色）。

## 蓝图用法

以下节点来自 `WaterEditor` 模块，主要面向编辑器流程。部分节点也可在运行时调用（如 `UJumpFloodComponent2D`）。

### 水体信息获取与缓存

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetWaterBodies` | 获取影响当前地形画笔的所有水体Actor（支持按子类筛选） | `AWaterLandscapeBrush` |
| `GetWaterBodyIslands` | 获取影响当前地形画笔的所有水体岛屿Actor | `AWaterLandscapeBrush` |
| `GetActorsAffectingLandscape` | 获取影响当前地形的所有水体画笔Actor（水体 + 岛屿） | `AWaterLandscapeBrush` |
| `SetActorCache / GetActorCache / ClearActorCache` | 为特定 Actor 设置/读取/清除缓存对象（用于存储画笔中间数据） | `AWaterLandscapeBrush` |

### 水体蓝图事件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BlueprintWaterBodiesChanged` | 当水体列表发生增删时触发，在编辑器中可重写执行自定义逻辑 | `AWaterLandscapeBrush` |
| `BlueprintWaterBodyChanged` | 当某个水体 Actor 属性改变时触发 | `AWaterLandscapeBrush` |
| `BlueprintGetRenderTargets` **(已弃用)** | 已被运行时 `WaterInfoTexture` 替代 | `AWaterLandscapeBrush` |

### 2D 距离场组件（JumpFlood）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMIDs` | 创建材质实例动态，用于跳步算法的材质 | `UJumpFloodComponent2D` |
| `AssignRenderTargets` | 分配两个临时渲染目标作为 ping-pong 缓冲区 | `UJumpFloodComponent2D` |
| `JumpFlood` | 从种子 RT 执行完整跳步距离场计算 | `UJumpFloodComponent2D` |
| `SingleJumpStep` | 执行一步跳步计算，返回当前结果 RT | `UJumpFloodComponent2D` |
| `FindEdges` | 从种子 RT 计算边缘距离场 | `UJumpFloodComponent2D` |
| `SingleBlurStep` | 执行一步模糊 | `UJumpFloodComponent2D` |
| `FindEdges_Debug` | 调试模式下将边缘结果输出到指定 RT | `UJumpFloodComponent2D` |

### 焦散网格与编辑器预览

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EditorTick` | 编辑器每帧调用（需启用 `SetEditorTickEnabled`） | `ACausticsGeneratorActor` |
| `SpawnWaterPreviewGrid` | 生成水网格预览用的 HISM 实例 | `ACausticsGeneratorActor` |
| `SpawnCausticParticleGrid` | 生成焦散粒子预览用的 HISM 实例 | `ACausticsGeneratorActor` |

## C++ 用法

### 头文件引入

```cpp
// WaterEditor 模块类
#include "WaterEditorModule.h"
#include "WaterBrushManager.h"
#include "JumpFloodComponent2D.h"
#include "WaterLandscapeBrush.h"
#include "WaterBodyActorFactory.h"
```

### 基本用法

**获取水体画笔管理器并查找影响地形的 Actor**  
该代码片段来源于 `AWaterLandscapeBrush` 的公开接口。

```cpp
// 假设存在一个 AWaterLandscapeBrush* BrushActor
TArray<AWaterBody*> OceanBodies;
BrushActor->GetWaterBodies(AWaterBodyOcean::StaticClass(), OceanBodies);

TArray<TScriptInterface<IWaterBrushActorInterface>> AllActors;
BrushActor->GetActorsAffectingLandscape(AllActors);
```

**创建 JumpFlood 组件并执行一次距离场计算**  
组件通常由 `AWaterBrushManager` 自动创建，也可手动附加到任意 Actor。

```cpp
UJumpFloodComponent2D* JumpFlood = NewObject<UJumpFloodComponent2D>(GetOwner());
JumpFlood->RegisterComponent();
JumpFlood->CreateMIDs();

// 分配两个渲染目标（128x128，PF_R8G8B8A8）
UTextureRenderTarget2D* RTA = NewObject<UTextureRenderTarget2D>();
RTA->InitCustomFormat(128, 128, PF_R8G8B8A8, false);
UTextureRenderTarget2D* RTB = NewObject<UTextureRenderTarget2D>();
RTB->InitCustomFormat(128, 128, PF_R8G8B8A8, false);
JumpFlood->AssignRenderTargets(RTA, RTB);

// 执行跳步距离场（种子RT需要事先填充）
JumpFlood->JumpFlood(SeedRT, 0.0f, FLinearColor::White, false, 0.0f);
```

### 进阶用法

**自定义水体画笔 Actor**  
继承 `AWaterLandscapeBrush` 并覆写 `BlueprintWaterBodiesChanged_Native` 以响应水体列表变化。

```cpp
// MyWaterBrush.h
#include "WaterLandscapeBrush.h"
#include "MyWaterBrush.generated.h"

UCLASS()
class AMyWaterBrush : public AWaterLandscapeBrush
{
    GENERATED_BODY()
public:
    virtual void BlueprintWaterBodiesChanged_Native() override
    {
        Super::BlueprintWaterBodiesChanged_Native();
        // 自定义逻辑：例如重新生成自定义纹理
        TArray<AWaterBody*> Rivers;
        GetWaterBodies(AWaterBodyRiver::StaticClass(), Rivers);
        UpdateRiverVelocityTexture(Rivers);
    }

private:
    void UpdateRiverVelocityTexture(const TArray<AWaterBody*>& Rivers) { /* ... */ }
};
```

## Demo 示例

以下是一个最小的 C++ 编辑器模块，演示如何在启动时注册自定义水体画笔行为。该示例假设项目已经启用 Water 插件，并且包含 `WaterEditor` 模块。

### MyWaterEditorModule.h

```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "WaterEditorModule.h"

class FMyWaterEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### MyWaterEditorModule.cpp

```cpp
#include "MyWaterEditorModule.h"
#include "WaterBrushManager.h"
#include "Engine/World.h"
#include "LevelEditor.h"

IMPLEMENT_MODULE(FMyWaterEditorModule, MyWaterEditor);

void FMyWaterEditorModule::StartupModule()
{
    // 监听世界创建，以便在需要时自动查找或创建 WaterBrushManager
    FLevelEditorModule& LevelEditor = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
    // 此处可注册自定义通知等
}

void FMyWaterEditorModule::ShutdownModule() {}
```

### 使用步骤

1. 在 `.Build.cs` 中添加对 `WaterEditor`、`Water`、`Landmass`、`Niagara` 的依赖（见下方模块依赖）。  
2. 在编辑器中打开一个含有地形的小关卡。  
3. 从放置面板拖拽“Ocean”、“River”、“Lake”或“Custom Water Body” Actor。  
4. 选中水体后，在细节面板的“Terrain”分类中调整雕刻参数，观察地形实时变化。  
5. 双击 `WaterWaves` 资源（或新建一个）打开波浪编辑器，调整波浪频谱。  

## 模块依赖

如果你的模块需要引用 Water 插件中的类（如 `AWaterBody`），请在 `Build.cs` 中添加如下依赖（仅列出独特模块）：

| 模块 | 用途 |
|---|---|
| `Water` | 运行时水体组件、Actor、可绘样条线等 |
| `Landmass` | 地形画笔与水体交互的底层支持 |
| `Niagara` | 水体粒子效果（水花、泡沫） |
| `GeometryProcessing` | 水体与地形的几何运算 |
| `BlueprintMaterialTextureNodes` | 水体材质节点蓝图 |

若仅使用 `WaterEditor` 模块（编辑器工具），还需添加 `UnrealEd`、`PropertyEditor` 等常见编辑器依赖，此处省略。

## 维护状态

### 近期更新

- 2025-10-02 `bfb2aaa5` — 后处理体积排序改进（间接影响水体后处理）
- 2025-09-23 `76aaaaf9` — [HWRT] 修复因 FWaterMeshSceneProxy 移动光线追踪几何体导致的崩溃
- 2025-09-23 `34fe4187` — 世界分区 HLOD：在 HLOD Actor 中存储 HLOD 构建报告属性
- 2025-09-03 `b34c0c64` — [Water] 修复三元操作符操作数类型不匹配的警告
- 2025-09-03 `9730d902` — [Water] 修复因缓存 FMaterialRenderProxy 而非 UMaterialInterface 导致的崩溃

### 维护评价

- **创建时间**：2025-09-03（约 0 年）
- **更新频率**：平均每月 1-2 次实质性修复/改进，近期包括崩溃修复、性能优化和向正式功能的迁移。
- **活跃度**：活跃维护中，有专门的 Water 团队持续优化。
- **局限性**：
  - 标记为 `IsExperimentalVersion=true`，API 可能不稳定，部分函数已废弃（如旧的 RenderTarget 回调）。
  - 需要手动启用（`EnabledByDefault=false`），且需依赖 Landmass、Niagara 等插件。
  - 大规模使用可能涉及性能调优（如水面距离场分辨率、Wave 频谱集成）。
- **推荐使用**：适合新项目或需要深度水体系统的大型游戏。若项目仅在早期原型阶段，可考虑使用更轻量的水体方案。请注意定期关注插件更新以跟进 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Water)
- [官方文档](https://docs.unrealengine.com/5.4/en-US/water-system-in-unreal-engine/)（通用水体系统文档，部分功能在实验性插件中）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Water/Source/WaterEditor/Private/Tests)