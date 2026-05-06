# UAF Mirroring

> Keyframe mirroring for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 镜像 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

---

## 用途

UAF Mirroring 是 UAF（Unreal Animation Framework）动画系统的扩展插件，提供关键帧镜像功能。它允许用户在 UAF 动画图中通过镜像数据表（`UMirrorDataTable`）将输入动画姿态进行镜像，例如将右臂动作自动镜像到左臂，从而简化对称动画的制作流程。

该插件解决以下问题：
- 避免为对称动作（如行走、攻击）分别制作左右两侧的关键帧。
- 在运行时或编辑器中动态应用镜像，提升动画制作效率。

---

## 使用场景

- **制作双足或四足角色的对称动画**：只制作一侧动画，通过镜像节点生成另一侧。
- **武器或道具的左右手切换**：在动画蓝图中根据手持物品自动镜像关键帧。
- **结合 UAF 动画系统**：在 UAF 的动画图（AnimGraph）中集成镜像节点，无需额外写代码。

---

## 蓝图用法

> 该插件主要提供 UAF 动画图中的镜像节点模板，蓝图用户可在 UAF 动画图中直接创建“Mirror”节点，并连接数据。

### 核心节点

| 节点               | 说明                                                                 | 所在类                            |
|-------------------|----------------------------------------------------------------------|-----------------------------------|
| `Mirror`          | 将输入动画关键帧按镜像数据表进行镜像输出。可设置镜像表、应用范围等参数。 | `UUAFGraphNodeTemplate_Mirror`    |

### 使用示例（蓝图描述）

1. 在 UAF 动画图中右键，选择 “UAF” → “Mirror” 节点。
2. 选中节点，在细节面板中设置 `MirrorDataTable` 为已创建的镜像数据表资产。
3. 将需要镜像的动画输入连接到节点的 `Input` 引脚。
4. 可选配置 `Setup` 和 `ApplyTo` 引脚以控制镜像参数。
5. 运行动画图，即可看到输出姿态已镜像。

---

## C++ 用法

### 头文件引入

```cpp
#include "UAFGraphNodeTemplate_Mirror.h"
```

### 基本用法

从测试用例提取的创建镜像节点示例：

```cpp
// 在 UAF 动画图控制器中创建镜像节点
UAnimNextController* Controller = GetAnimNextController();
UUAFGraphNodeTemplate_Mirror* MirrorTemplate = NewObject<UUAFGraphNodeTemplate_Mirror>();
URigVMUnitNode* MirrorNode = Controller->AddUnitNode(MirrorTemplate, FText::FromString("MirrorNode"));

// 设置镜像数据表（也可在节点创建时直接拖放资产）
UMirrorDataTable* MirrorTable = LoadObject<UMirrorDataTable>(nullptr, TEXT("/Game/Animations/MyMirrorTable"));
if (MirrorTable)
{
    Controller->OpenUndoBracket(TEXT("Set Mirror Table"));
    Controller->SetNodeTitle(MirrorNode, FText::Format(LOCTEXT("NodeTitleFormat", "Mirror using {0}"), FText::FromString(MirrorTable->GetName())).ToString(), true, true, true);
    Controller->CloseUndoBracket();
}
```

**来源**: `Engine/Plugins/Experimental/UAF/UAFMirroring/Source/UAFMirroringUncookedOnly/Private/UAFGraphNodeTemplate_Mirror.h`

### 进阶用法

支持资产拖放：用户可以从内容浏览器将 `UMirrorDataTable` 直接拖放到镜像节点上，自动配置节点标题。

```cpp
// 处理资产拖放的虚函数实现
virtual void HandleAssetDropped_Implementation(UAnimNextController* Controller, URigVMUnitNode* Node, UObject* Asset) const override
{
    // 设置节点标题为“Mirror using <资产名>”
}
```

---

## Demo 示例

由于该节点依赖 UAF 动画图系统，无法提供完全独立的编译示例。以下展示在自定义 UAF 模块中注册并使用镜像节点的最小框架：

**MirrorSetup.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UAFAnimNodeTemplate.h"
#include "MirrorSetup.generated.h"

UCLASS()
class UMyMirrorSetup : public UUAFGraphNodeTemplate_Mirror
{
    GENERATED_BODY()
public:
    UMyMirrorSetup() { /* 自定义属性 */ }
};
```

然后在动画图控制器创建节点即可。完整实现需参考 UAF 官方示例。

---

## 模块依赖

以下依赖为使用该插件时需要的模块（省略常见依赖）：

| 模块               | 用途                              |
|-------------------|-----------------------------------|
| `UAF`             | 核心动画框架                       |
| `UAFAnimGraph`    | 动画图编辑与运行时支持              |
| `AnimGraphUncookedOnly` | 提供图节点模板基类与控制器功能 |

> **注意**：常见依赖（Core, Engine, Slate 等）已省略。

---

## 维护状态

### 近期更新

- 2025-08-20 `da73fa04` — Fixed aborting mirror task entirely when skipping mirroring attributes or bones but still have other mirrors (修复跳过镜像属性或骨骼时完全中止镜像任务的问题)
- 2025-08-20 `c983bdd2` — UAF Mirroring improvements (镜像功能改进)
- 2025-08-18 `e8a6162f` — First pass for mirroring support in UAF (首次添加 UAF 镜像支持)

### 维护评价

- **创建时间**：2025-08-18，距今不足 1 个月（截至 2025 年预计 9 月），属于全新插件。
- **最近更新**：最近两天内有多次功能性提交，修复和增强。
- **活跃程度**：高活跃度，正在快速迭代开发中。
- **已知问题**：实验性标签表明 API 尚未稳定，可能发生变更。
- **推荐使用**：适用于需要使用 UAF 动画系统并希望快速集成镜像功能的项目；但需注意其实验性质，生产环境中需谨慎测试。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMirroring/Tests)（未提供，实际路径可能位于插件内或 UAF 测试目录）