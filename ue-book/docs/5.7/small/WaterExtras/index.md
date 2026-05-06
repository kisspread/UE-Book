# Water Extras

> Samples, test maps, etc intended to help developers start using the water system. Not intended to be used directly in a shipping product.

| 属性 | 值 |
|---|---|
| 中文名 | 水系统示例 |
| 分类 | Water |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产、测试地图、蓝图资源） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WaterExtras) | |

## 用途

Water Extras 是一个**纯内容**插件，不包含任何 C++ 代码或新的运行时功能。它的目的是提供一系列**示例地图**、**演示关卡**和**蓝图资产**，帮助开发者快速上手和理解 UE5 的水系统（Water System）的用法。插件中包含了各种水体的配置示例、材质设置、以及如何将水系统集成到场景中的最佳实践。由于它被标记为实验性且不适用于最终产品，其主要价值在于学习和测试，而非直接用于商业游戏。

## 使用场景

- 你在学习 UE5 的水系统（Ocean、Lake、River 等组件），需要直观的范例。  
- 你想了解如何在水体表面添加浪花、泡沫等视觉效果。  
- 你需要测试水系统在不同地形和光照条件下的表现。  
- 你希望快速搭建一个包含基础水体功能的测试关卡进行迭代。

## 蓝图用法

该插件**没有**暴露任何自定义的蓝图可调用函数（UFUNCTION(BlueprintCallable)）或蓝图读写属性（UPROPERTY(BlueprintReadWrite)），因为它本身不包含逻辑代码。插件中的所有行为均通过放置在地图中的 Water 系统原生组件（如 `Ocean`, `Lake`, `River`）以及配套的材质实例和蓝图资产（如 `BP_WaterExtras_Example`）来实现，用户可以直接在这些资产的基础上修改或参考。

### 核心内容

| 资产 | 说明 | 位置 |
|---|---|---|
| 示例地图 | 包含不同水体类型（海洋、湖泊、河流）的演示世界 | `Content/Maps/` |
| 材质实例 | 预设的水面材质参数（颜色、波浪、泡沫） | `Content/Materials/` |
| 蓝图示例 | 展示如何通过蓝图动态修改水体属性 | `Content/Blueprints/` |

## C++ 用法

无（纯内容插件）。不提供 C++ API 或模块。

## Demo 示例

由于插件不含 C++ 代码，仅能够通过编辑器中的示例关卡进行演示。

操作步骤：  
1. 在 UE5 编辑器中启用 "Water Extras" 插件（设置 → Plugins → Water 分类下）。  
2. 重启编辑器后，打开 "内容浏览器" → 选择插件内容目录（`Plugins/WaterExtras Content`）。  
3. 加载任意示例地图（例如 `/WaterExtras/Maps/WaterExtras_Demo`）。  
4. 观看预设的水体场景，并打开其中的蓝图实例查看实现方式。

## 模块依赖

无（纯内容插件，无需额外模块依赖）。

| 模块 | 用途 |
|---|---|
| `Water`（依赖插件） | 核心水系统插件，Water Extras 的全部内容均以此为基础运行 |

若要使用该插件中的资产，您的项目必须启用 `Water` 插件。

## 维护状态

### 近期更新

- 2022-10-21 `610c467` 将内置插件的 vendor 链接更新为安全协议  
- 2021-11-18 `0c3be2b` 合并 Release-Engine-Staging 到 Test（初始引入）

以上为全部 git 记录。自 2022-10-21 起，插件内容本身**未再更新**。

### 维护评价

Water Extras 是一个实验性、纯内容的辅助插件，自引入以来仅有一次非功能性的提交（链接协议更新），其示例内容和地图很可能基于 UE5 早期版本（如 5.0/5.1）的水系统设计。目前该插件在 UE 5.7 等后续版本中仍可加载，但可能无法反映水系统的最新改进（如 5.3 引入的 Wave Simulation 等）。

- **创建时间**：2021-11-18（约 4 年）  
- **最近更新**：2022-10-21（超过 2 年没有实质性内容更新）  
- **活跃度**：维护不活跃，可视为**可能废弃**  
- **推荐使用**：对于快速学习基础水系统功能有一定帮助，但不建议依赖其内容作为生产项目的基础；更推荐直接使用官方的 `Water` 插件及最新官方示例。

⚠️ 警告：插件已超过 1 年无实质性更新，内容可能与最新引擎版本存在差异。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WaterExtras)  
- 官方文档：无（`.uplugin` 中未填写 DocsURL）  
- 测试用例：无（该插件不包含自动化测试）