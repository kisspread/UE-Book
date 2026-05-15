---
title: Awesome UE5 Tools 
comments:  true
---

# Awesome UE5 Tools
Including open source and non-open source, commercial and non-commercial.

> 是否awesome，需要根据个人需求来判断。另外，第三方工具选择需要慎重~

> 💡 **收录开源库**：[提交 Issue](https://github.com/kisspread/UE-Book/issues/new?template=library-submission.yml)，填写 GitHub 地址即可，AI 自动审核写入。

## Editor Tools

- [NanoGaussianSplatting](https://github.com/TimChen1383/NanoGaussianSplatting)  Nanite-Style Gaussian Splatting Render
  - 在 Unreal Engine 中实现实时大规模 3D Gaussian Splatting（类似 Nanite 风格），适合游戏、模拟和交互演示，支持大场景粒子光照渲染。

- [BlenderTools](https://github.com/poly-hammer/BlenderTools) Blender Tools for Unreal Engine
  ![alt text](https://raw.githubusercontent.com/poly-hammer/BlenderTools/main/docs/images/send2ue/4.gif)
  - 一键把 Blender 中的资产直接发送到 Unreal Engine。支持类型：静态网格（含 LOD）、骨骼网格、动画序列、Groom 毛发（Alembic）等。
  - 可以快速把 Unreal Marketplace 里的角色/动画重定向到 Blender 的 Rigify 骨骼上，并直接在 Blender 中创作新动画

- [Blender-For-UnrealEngine-Addons](https://github.com/xavier150/Blender-For-UnrealEngine-Addons) export asset from Blender to Unreal Engine
  - 一键把 Blender 中的资产导出到 Unreal Engine，极大简化游戏开发 pipeline，节省大量时间

- [K2PostIt](https://github.com/HomerJohnston/K2PostIt) This is a fairly small plugin which is intended to look down upon Unreal's very annoying "Comment" node. Don't get me wrong, the "Comment" node is great for wrapping/labelling blocks of blueprint graph, but it's hardly a comment node!
  ![alt text](/libraries/images/00_image-80.webp)
  - 一个更加强大，好看的注释工具，支持Markdown

- [Yap](https://github.com/HomerJohnston/Yap) Yap is a project-agnostic dialogue engine running on FlowGraph. It is being built by studying games like Monkey Island to try and recreate their capabilties. It is usable via any combination of blueprint or C++, although you will need a C++ project to build this plugin.
  ![alt text](/libraries/images/00_image-83.webp)
  - 一个基于FlowGraph的对话引擎，支持蓝图和C++





- [CustomShortcuts](https://github.com/Adrien-Lucas/CustomShortcuts)Custom Shortcuts is a plugin initially released to UE5 to allow designers to make their own editor shortcuts by executing blueprint editor code.
  ![alt text](/libraries/images/00_image-84.webp)


- [EnhancedPalettePlugin](https://github.com/aquanox/EnhancedPalettePlugin) Enhanced Palette Plugin for Unreal Engine extends capabilities of Place Actors panel
  ![alt text](/libraries/images/00_image-82.webp)
  - 该插件扩展了虚幻编辑器 Place Actors 面板的功能，允许从编辑器设置中进行自定义，并授予动态生成类别内容的能力。



- [MDViewModel](https://github.com/DoubleDeez/MDViewModel) An Unreal Engine 5 Model-View-ViewModel Plugin with automatic data binding to use in UMG Widget, Actor, and Object Blueprints
  - 另一个UE的MVVM框架，支持actor、blueprint、UMG、object blueprints
  ![alt text](/libraries/images/00_image-77.webp)

- [SubsystemBrowserPlugin](https://github.com/aquanox/SubsystemBrowserPlugin) Plugin that adds a Subsystem Browser panel for Unreal Engine Editor to explore running subsystems and edit their properties.
  ![alt text](/libraries/images/00_image-79.webp)
  - 一个查看 Subsystem 的工具,用于探索正在运行的子系统并编辑其属性



- [BlueprintComponentReferencePlugin](https://github.com/aquanox/BlueprintComponentReferencePlugin) Blueprint Component Reference Plugin provides a struct and set of accessors that allow referencing actor components from blueprint editor details view with a component picker, it automatically identifies context and builds list of components for selection menu.
  - 在编辑器里，当你有一个 UPROPERTY 要保存某个组件引用时，这个插件能自动列出目标 Actor 的组件选项供你选择，而不是手动输入或硬编码
  ![alt text](/libraries/images/00_image-75.webp)


- [QuickActions](https://github.com/outoftheboxplugins/QuickActions) Find Anything Inside Unreal Editor Quick
  ![alt text](/libraries/images/00_image-74.webp)
  - :::details 作者赠言
    If you want to:
    Find and execute actions within Unreal in seconds without using your mouse

    Increase your productivity by quickly accessing recent and favorite commands

    Interact with Unreal's built-in functionality in a more user-friendly manner

    Learn more about the tools by viewing their assigned shortcuts & detailed tooltips

    Create your own automation scripts to simplify your workflows

    Then I encourage you to keep reading, this product might be for you.

    The true reason people love Apple products

    "Apple products just work."

    If you ask Apple users why they why they made their choice, there is a 80% chance this is the answer you will get.

    After running this experiment on Twitter one day, I can confirmed that's the case.

    The next day I went to the closest Apple Store to test out a MacBook 16inch Pro.

    That's when I discovered the Spotlight Search.

    That tool was so fast, fun and reliable to use.

    I thought to myself: "This is the best thing ever, I need to bring it to Unreal Engine".

    I have to admit, it was a lot more complicated than I anticipated and required much more work.

    After a few months of late nights and a few more research trips to the Apple Store, I finally had something to show.

    It wasn't anywhere near perfect, but the feedback I got from the community was incredible. It confirmed my assumption people will love it.

    The reactions were enough to keep me going and I pour more and more time into it. 

    My Dream

    On my journey to develop this tool, I've met some incredible people along the way. I am grateful for every single like, comment, retweet, dm or feedback received.

    I hope one day this amazing tool will get fully integrated in the Unreal Engine.

    Until that day, this plugin will remain here on the marketplace for free and open-sourced on GitHub.

    I realized this is a much bigger project than I can take on my own.

    Feel free to Contribute, steal, or do whatever you please with it.
    :::
  - 仿MacOS的快捷操作，类似JetBrains的双击shift搜索
  - 除了查找各种资产，还可以执行各种内置的命令，动作
  - fab https://www.fab.com/listings/7b9e1f59-9367-4851-8aaf-a0479cd976be
  - 文档 https://outofthebox-plugins.notion.site/Quick-Actions-28b7a364109441779f11d1e6f5f75658

- [SlateStyleBrowser](https://github.com/sirjofri/SlateStyleBrowser) This small tool lets you browse Unreal Engine's Slate styles easily, search for specific ones and copy slate code for the selected style or brush.
  - 这个小工具可以让你轻松浏览虚幻引擎的Slate样式，搜索特定的样式，并复制选定样式或笔刷的Slate代码。
  - ![alt text](/libraries/images/00_image-73.webp)

- [PropertyWatcher](https://github.com/guitarfreak/PropertyWatcher) A runtime variable watch window for Unreal Engine using ImGui.
  - 不是插件，是一个Imgui使用的代码案例
  ![alt text](/libraries/images/00_image-76.webp)



- [ImGuiPlugin](https://github.com/amuTBKT/ImGuiPlugin) A simple plugin for integrating Dear ImGui in Unreal Engine 5.
  <!-- <video controls src="../assets/images/amutbk_imgui3.mp4" title="Title"></video> -->
  - 来自 [amu_mhr](https://x.com/amu_mhr) 的 UE5 ImGui 集成
  - 和其他 ImGui Plugin 不同的是，它通过套了一层 Slate Widget 来实现类型原生widget的dock效果
  - 更好看的UIShader
  - 附带一个 example： https://github.com/amuTBKT/ImGuiExamples
 

- [ImGui](https://github.com/VesCodes/ImGui) Supercharge your Unreal Engine development with Dear ImGui. This plugin is designed to be as frictionless and easy to use as possible while seamlessly integrating all of ImGui's features into UE's ecosystem.
  ![alt text](/libraries/images/00_image-78.webp)
  - 另一个imgui，支持Multiple Viewports, Docking, Editor Support, Play-in-Editor, Remote Drawing
  - 这里的docking是指 `Dear ImGui` 的 原生的 docking 功能，而不是通过 Slate Widget 来实现的 dock 效果
  - 多视口功能允许您将 Dear ImGui 窗口无缝地从主渲染上下文中提取出来 。在传统的游戏编程中，您的引擎/游戏通常会创建一个与图形上下文（例如使用 DirectX、OpenGL）关联的操作系统窗口，并且所有渲染都必须在此图形上下文中进行。除此之外，多视口还方便在多个显示器上使用 Dear ImGui。
  - 在程序和独立 Slate 应用程序中使用 ImGui

- [UnrealImGui](https://github.com/IDI-Systems/UnrealImGui) Unreal plug-in that integrates Dear ImGui framework into Unreal Engine 4/5.
  - IDI-Systems 的 ImGui 集成,最多人用的版本
  - Docking branch of Dear ImGui is correspondigly available on docking branch kept in sync with master as much as possible.









- [RaylibUE](https://github.com/DarknessFX/RaylibUE) Bridge Raylib's easy-to-use drawing API with Unreal Engine's intuitive Blueprint nodes.
  - 特定场景下有用：用一个 独立的渲染叠加层（overlay） 在 Unreal 的游戏视口上渲染。这样它的绘图是“叠加”在 Unreal 渲染结果上，而不是修改 Unreal 的渲染管线。

- [DFoundryFX](https://github.com/DarknessFX/DFoundryFX) Unreal Engine 5.6 Plugin with Dear ImGUI, customizable performance metric charts (including Shipping builds), Shader compiler monitoring and STAT commands control panel for Unreal Engine GameViewports.
  - Unreal Engine 里常用的 STAT（统计／调试）命令，比如 STAT GPU、STAT CPU、STAT Scene 等，通常是通过控制台或命令行执行，这个插件提供一个面板来控制它们，更方便在 Game Viewport 里直接切换／查看
  - 可以看到 Shader 编译过程／状态。比如什么时候 Shader 在后台编译、编译进度、是否有延迟或瓶颈

  
- [PropertyHistory](https://github.com/VoxelPlugin/PropertyHistory) Property History allows you to quickly see the history of a property. It works with most objects in Unreal: actors, material nodes, material instances... More advanced properties like arrays, map, sets and instanced structs are also supported.
  ![alt text](/libraries/images/00_image-67.webp)
  - VoxelPlugin出品，必属精品，用于查看属性的历史记录

- [ProjectCleaner](https://github.com/ashe23/ProjectCleaner) Unreal engine plugin for managing all unused assets and empty folders in project.
  - 用于清理未使用的资源和空文件夹
  ![alt text](/libraries/images/00_image-60.webp)


- [UEToolboxPlugin_Dev](https://github.com/gradientspace/UEToolboxPlugin_Dev) This repository contains a development setup for the Gradientspace UEToolbox plugin. The repo for that plugin only contains the plugin code, which must be built inside a UE5 project. So, this repo contains such a project, configured with some test levels and assets that are useful for checking that (eg) building and packaging works properly. Scripts for packaging the plugin for distribution on the FAB marketplace are also included.
  - https://github.com/gradientspace/UEToolboxPlugin 这个是独立插件，上面的是示例项目
  - 作者Ryan Schmidt（Gradientspace）曾在Epic Games工作，是Modeling Mode (建模模式) 和 Geometry Script (几何脚本)，以及DynamicMesh3的核心开发者
  - 该插件从闭源到开源的心路历程，值得细品：https://www.gradientspace.com/tutorials/2025/8/3/uetoolbox-parametric-assets-and-opensource
  - >不幸的是，就我个人的抱负而言，Epic Games Inc 对“运行时工具”方面并不特别感兴趣。虚幻是用于游戏的游戏引擎，让世界上一些最优秀的游戏引擎开发者也关心如何将其打造成一个用于创作工具的实时引擎，这……很有挑战性。我一直主张，这就是我们将在《堡垒之夜》创意版中构建更高级编辑工具的方式，但当 Epic 转向专注于 UEFN（堡垒之夜虚幻编辑器）时，这个方向就夭折了。这就是为什么“如何在运行时使用 ITF”只能在本网站的文章（附件 A和附件 B）中了解，而你很难在 Epic 找到任何人承认这是可能的。
  - > 在 Epic 的 Lyra 项目中，我们拼凑了一个系统，用于追踪程序化 DynamicMeshActor (DMA) 与烘焙的 StaticMesh 以及放置的 StaticMeshActors 之间的关系，并且可以“交换” DMA 来代替 StaticMesh 进行实时编辑。但 DMA 必须存在于关卡中——我们的“交换”操作将它们隐藏在地平面以下很远的地方。完全是黑客行为。此外，追踪系统存在于关卡中，不支持多用户编辑，导致了大量问题。在 Epic 内部，我发现另一种方法变得流行起来，即使用纯编辑器的 ChildActorComponent 和程序化生成器，该生成器会烘焙到父 Actor 的 StasticMesh 中。但这只适用于单个实例，并且存在自身的问题。
  - ![alt text](/libraries/images/00_image-56.webp)


- [NodeToCode](https://github.com/protospatial/NodeToCode) Translate Unreal Engine Blueprints to C++ in seconds. Not hours.
  - Node to Code只需单击一下即可将您的虚幻引擎蓝图图表转换为简洁、结构化的 C++ 代码。无需再花费数小时进行繁琐的手动转换，无需费力解释复杂的视觉逻辑，也无需在庞大的蓝图系统中导航。无论您是要优化性能、改进协作，还是学习/教授虚幻引擎 C++ API，这款由 LLM 提供支持的插件都能帮助您轻松完成蓝图到代码的转换。
  - ![alt text](https://github.com/protospatial/NodeToCode/raw/main/assets/Image_NodeToCode_BlueprintTranslation.gif)

- [BlueprintRetarget](https://github.com/PipeRift/BlueprintRetarget) An small tool that allows retargeting invalid blueprints when its parent class is missing on UE4

- [RVisualNarrative](https://github.com/Srkmn/RVisualNarrative) RVisualNarrative 是一款为虚幻引擎(Unreal Engine)开发的跨版本对话状态机编辑器插件，旨在提供可视化、灵活且高效的剧情对话编辑或者状态机解决方案。

- [CrystalNodes](https://github.com/SkylakeOfficial/CrystalNodes/wiki) Crystal Nodes contains a simple module that changes your blueprint graph style. It uses custom material as slate brush and is compatible with blueprint wiring plugins. This may have little performance impact, but it's acceptable. The plugin does not tick when playing in editor or simulating.
  - ![alt text](/libraries/images/00_image-68.webp)

- [UE_TAPython](https://github.com/cgerchenhp/UE_TAPython_Plugin_Release) TAPython is an editor plugin for Unreal Engine. It provides a framework for creating python editor tools in Unreal Engine, and live Slate editing for developers, which makes creating menus and UE native Slate UI much easier and faster(without any compiling time or restart editor). The plugin also provides 200+ editor tool interfaces to use, making developing UE editor tools very simple and efficient.
  - 并非开源项目，但免费使用，看着很多增强的编辑器插件，我还没有尝试
  - ![alt text](/libraries/images/00_image-7.webp)


- [BPCorruptionFix](https://github.com/rweber89/BPCorruptionFix) Sometimes BPs get corrupted, due to Actor Component changes. Their type, their name, declaring them with the wrong properties, saving information about them inside of BPs … there are a number of ways this can happen.
  - 有用，但不常用

- [AdvancedUI](https://github.com/nikkomiu/AdvancedUI) 修改并保存UE编辑器的默认缩放比例。 Unreal Engine 5 Advanced UI Editor. it to start working This Unreal Engine Plugin allows setting a custom and persistent UI scale for the editor as well as allowing you to disable Slate UI tooltips in the editor (probably only useful for Linux).
  - 目前只有保存缩放比例的这一个功能。

- [UE-ProgramBrowser](https://github.com/SkecisAI/UE-ProgramBrowser)  Create, Build, Pakcage an Unreal Engine Standalone Program Application. 使用虚幻引擎（Unreal Engine）提供的资源创建独立应用程序（Standalone Program）而非游戏（Not Game），本插件实现了对独立应用程序从创建到打包的一键式流程管理
  - ![alt text](/libraries/images/00_image-8.webp)
  - ![alt text](/libraries/images/00_image-9.webp)
  - 更多参考 [https://zhuanlan.zhihu.com/p/391228179](https://zhuanlan.zhihu.com/p/391228179)

- [UEGitPlugin](https://github.com/ProjectBorealis/UEGitPlugin) Unreal Engine Git Source Control Plugin (refactored)

- [PCG Assets](https://github.com/TimChen1383/PCGAsset.git) 大量PCG C++自定义节点资产
  - ![alt text](/libraries/images/00_image-11.webp)

- [WFCLevelCreator](https://github.com/alwayswinder/WFCLevelCreator) UE5 WFC 算法生成地图
  - https://www.bilibili.com/video/BV1jz421C7bS/ 还可以参考他自定义slate ui 的实现，作者很有干货
  - ![alt text](/libraries/images/00_image-10.webp)


- [动画纹理](https://github.com/neil3d/UAnimatedTexture4) 直接把GIF作为为一种资产 This plugin allows you to import animated GIF into your Unreal Engine 4 project as a new AnimatedTexture asset type.
  - ![alt text](/libraries/images/00_image-12.webp)

- [Renom](https://github.com/UnrealisticDev/Renom) UE5改名工具 A simple tool to rename Unreal Engine projects.
  - (实测不是很好用, 可能是项目自身原因)

- [MDMetaDataEditor](https://github.com/DoubleDeez/MDMetaDataEditor) 支持使用蓝图修改、配置元数据。Unreal Engine 5.1+ plugin to enable editing meta data of Blueprint Properties, Functions, and Function and Event Parameters

- [RefreshAllNodes](https://github.com/nachomonkey/RefreshAllNodes) 该插件在编辑器中创建一个按钮，它将在所有蓝图上运行内置的“刷新所有节点”命令。Unreal Engine plugin that refreshes and compiles all of your blueprints.
  - 只有一个按钮，点击了会刷新全部蓝图文件。

- [Cog](https://github.com/arnaud-jamin/Cog) 基于Dear ImGui的UE调试工具集合。Cog is a set of debug tools for Unreal Engine built on top of Dear ImGui
  - 提供比UE原版更好用的GAS、EnhancedInput、行为树、CheatMenu等调试工具。
  - ![alt text](/libraries/images/00_image-13.webp)

- [Minesweeper](https://github.com/GapingPixel/Minesweeper) Minesweeper Editor Tool. Fully made with Slate
  - Slate 实现的扫雷游戏
  - ![alt text](/libraries/images/00_image-4.webp)


- [EnhancedAsyncActionPlugin](https://github.com/aquanox/EnhancedAsyncActionPlugin)  Experimental plugin featuring lambda-like capture of data for blueprint async nodes
  ![EnhancedAsyncActionPlugin screenshot](https://raw.githubusercontent.com/aquanox/EnhancedAsyncActionPlugin/main/Images/EAA-CaptureProblem.png)
  ![EnhancedAsyncActionPlugin screenshot](https://raw.githubusercontent.com/aquanox/EnhancedAsyncActionPlugin/main/Images/EAA-CaptureProblemOut.png)
  ![EnhancedAsyncActionPlugin screenshot](https://raw.githubusercontent.com/aquanox/EnhancedAsyncActionPlugin/main/Images/EAA-ImitationWithStructs.png)
  - 💬 这是一个针对 Unreal Engine 5 蓝图异步节点的实验性插件，通过自定义 K2Node 和 FInstancedPropertyBag 简化了数据捕获过程，适用于需要处理复杂异步逻辑的蓝图开发者，但实验性质意味着可能需要进一步测试和优化。

- [UnrealBridge](https://github.com/TornLux/UnrealBridge)  Typed control surface for Unreal Engine that lets AI agents introspect assets, author Blueprints/AnimBPs, and edit levels — with reactive events and undoable writes.
  - UnrealBridge 是一个为 Unreal Engine 设计的类型化控制表面，专为 AI 代理打造。它允许 AI 代理检查资产、创建蓝图和动画蓝图，并编辑关卡，同时支持反应式事件订阅和可撤销的写入操作。
  - 💬 该项目针对 AI 代理与 Unreal Engine 的交互提供了结构化接口，AST 预检查机制能有效减少幻觉错误，适合自动化内容创作和编辑场景，但依赖特定 UE 版本且主要面向 Windows 平台。
  🔗 [Agent Skills open standard](https://www.agensi.io/learn/agent-skills-open-standard)

- [GaussianSplattingForUnrealEngine](https://github.com/Italink/GaussianSplattingForUnrealEngine)  A Unreal Engine plugin to convert primitives into high-quality 3D Gaussian point clouds.
  ![GaussianSplattingForUnrealEngine screenshot](https://raw.githubusercontent.com/Italink/GaussianSplattingForUnrealEngine/main/Resources/3dgs.gif)
  ![GaussianSplattingForUnrealEngine screenshot](https://raw.githubusercontent.com/Italink/GaussianSplattingForUnrealEngine/main/Resources/image-20250425144116238.png)
  ![GaussianSplattingForUnrealEngine screenshot](https://raw.githubusercontent.com/Italink/GaussianSplattingForUnrealEngine/main/Resources/image-20250125114152866.png)
  - 💬 这是一个将前沿的3D高斯溅射技术深度集成到虚幻引擎工作流中的插件，提供了从场景捕获、模型训练到在UE内实时渲染的完整解决方案。亮点在于其提供的深度修剪和LOD策略，试图解决3DGS在工业应用中的常见痛点。主要面向对实时渲染和视觉代理有较高要求的技术美术或图形程序员。
  🔗 [此处](https://drive.google.com/file/d/1gyKlCQacUsZUX6rXSKW1joyVxIYsBnHM/view?usp=drive_link) · [此处](https://www.bilibili.com/video/BV1GUwNeYE6c) · [colmap](https://github.com/colmap/colmap)

- [Blueprint_C](https://github.com/Italink/Blueprint_C)  Unreal Engine plugin for generating C++ code proxies from blueprints.
  ![Blueprint_C screenshot](https://raw.githubusercontent.com/Italink/Blueprint_C/main/Resources/93187154-e3f7-4db8-8672-cb497d3a31b4.png)
  ![Blueprint_C screenshot](https://raw.githubusercontent.com/Italink/Blueprint_C/main/Resources/image-20250408185302805.png)
  ![Blueprint_C screenshot](https://raw.githubusercontent.com/Italink/Blueprint_C/main/Resources/image-20250408185731888.png)
  - 💬 该项目为Unreal Engine开发者提供了一个实用的工具，通过自动生成C++代码代理来简化蓝图与C++之间的交互，适用于需要高性能或频繁跨语言调用的场景。但生成的代码可能需要手动调整以适应项目需求。

- [BlueLine](https://github.com/gregorik/BlueLine)  A comprehensive Blueprints plugin for UE5.6+
  ![BlueLine screenshot](https://ko-fi.com/img/githubbutton_sm.svg)
  ![BlueLine screenshot](https://github.com/user-attachments/assets/c565216f-c9fe-44dc-96c7-b1bb658e218e)
  - 💬 这是一个针对 Unreal Engine 蓝图编辑器的增强插件，通过强制电路板式布局和语义标记来优化蓝图代码可读性，适合需要整洁蓝图的 UE 开发者。但项目仍处于早期版本，功能完整性和社区采用度有待观察。
  🔗 [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg) · [Discord support](https://discord.gg/nqYQ5mtmHb) · [This repository deals with advanced bypasses of standard Unreal C++, Level Editor & Blueprint bottlenecks. 🟢 Currently available for B2B consulting and remote contract/Co-Dev integration (CET Timezone). [Contact form.](https://gregorigin.com/contact.html)

- [ImGuiWidgets](https://github.com/amuTBKT/ImGuiWidgets)  A collection of tools and widgets using ImGui plugin for Unreal Engine
  ![ImGuiWidgets screenshot](https://raw.githubusercontent.com/amuTBKT/ImGuiWidgets/master/Gallery/tool_texture_visualizer.png)
  ![ImGuiWidgets screenshot](https://raw.githubusercontent.com/amuTBKT/ImGuiWidgets/master/Gallery/tool_material_stats.png)
  ![ImGuiWidgets screenshot](https://raw.githubusercontent.com/amuTBKT/ImGuiWidgets/master/Gallery/tool_stats_visualizer.png)
  - 基于ImGui的Unreal Engine插件扩展，提供纹理可视化器、材质统计、状态可视化器、Niagara GPU分析器等开发调试工具，以及资产选择器、类选择器等编辑器控件。
  - 💬 实用的UE开发调试工具集，封装了多个常用调试功能到ImGui界面中，对图形程序员和性能优化工作有实际价值，但项目规模较小且依赖另一个ImGuiPlugin。
  🔗 [ImGui](https://github.com/amuTBKT/ImGuiPlugin) · [steps](https://github.com/amuTBKT/ImGuiPlugin#installation)

- [unDAW](https://github.com/Amir-BK/unDAW)  Editor and Runtime modules that aim to add some Digital Audio Workstation capabilities to Unreal Engine 5.
  - unDAW 是一个为 Unreal Engine 5 开发的插件，旨在为其添加数字音频工作站（DAW）的核心功能。它利用 Metasound 和 Harmonix 插件，允许用户通过简单的操作动态创建能播放 MIDI 文件的 Metasound，并支持实时编辑 MIDI 和为不同音轨分配不同的音频补丁。
  - 💬 这是一个概念明确且具有扩展潜力的 UE5 音频工具，其亮点在于将 DAW 工作流（如钢琴卷帘、混音器）集成到编辑器中，并借助 Metasound 系统实现。不过，从 README 可以看出项目仍在积极开发中，部分功能尚未完成或维护，稳定性有待观察。
  🔗 [SMUFL Fonts - Bravura](https://github.com/steinbergmedia/bravura)



## Animation

- [TurboSequence](https://github.com/LukasFratzl/TurboSequence) 用GPU加速骨骼动画 Skeletal Based GPU Crowds for UE5 🚀
  - ![alt text](/libraries/images/00_image-14.webp)

- [mixamo_converter](https://github.com/enziop/mixamo_converter) mixamo 根动画转换神器。 Blender addon for converting mixamo animations to Unreal 4 rootmotion

- [ALSXT](https://github.com/Voidware-Prohibited/ALSXT) Advanced Locomotion System Refactored with expanded Character States, Improved Foot Print system, Sliding, Vaulting and Wallrunning(XT)
  - ![alt text](/libraries/images/00_image-16.webp)

- [风动骨骼布料物理](https://github.com/SPARK-inc/SPCRJointDynamicsUE4) Real looking cloth physics engine for Unreal.
  - ![alt text](/libraries/images/00_image-15.webp)

- [KawaiiPhysics ](https://github.com/pafuhana1213/KawaiiPhysics) 低计算成本物理动画模拟。Kawaii Physics is a pseudo-physics plugin for Unreal Engine 4 and 5. It allows you to create simple and cute animations for objects like hair, skirts, and breasts.
  - ![alt text](/libraries/images/00_image-17.webp)

- [ThreepeatAnimTools](https://github.com/threepeatgames/ThreepeatAnimTools) 该存储库包含 Unreal 5.4+ 曲线编辑器过滤器和经过大量修改的 MetaHuman 角色选择器，适用于 Metahuman 和基于 UE5-Mannequin 的控制装置。 This repository contains Unreal 5.4+ curve editor filters and a heavily-modified MetaHuman character picker that works for both Metahuman and UE5-Mannequin-based control rigs.
  - ![alt text](/libraries/images/00_image-18.webp)

- [ProceduraAnim](https://github.com/alwayswinder/ProceduraAnim) UE5程序化动画例子，四足机器人演示
  - https://www.bilibili.com/video/BV1xY2NYUEau/ 林佬作品，干货很多
  - ![alt text](/libraries/images/00_image-19.webp)

- [SimpleRideControl](https://github.com/alwayswinder/SimpleRideControl) 仿老头环上马动画和镜头控制
  - https://www.bilibili.com/video/BV1nw411s7fU/ 
  - ![alt text](/libraries/images/00_image-20.webp)

- [UAnimatedTexture5](https://github.com/neil3d/UAnimatedTexture5)  A plugin that lets you import animated GIF and WebP images into Unreal Engine 5 as a new AnimatedTexture asset type.
  ![UAnimatedTexture5 screenshot](https://raw.githubusercontent.com/neil3d/UAnimatedTexture5/master/Docs/images/demo.png)
  ![UAnimatedTexture5 screenshot](https://raw.githubusercontent.com/neil3d/UAnimatedTexture5/master/Docs/images/mtl.png)
  ![UAnimatedTexture5 screenshot](https://raw.githubusercontent.com/neil3d/UAnimatedTexture5/master/Docs/images/umg.png)
  - 💬 针对 UE5 的动画纹理插件，填补了引擎原生不支持导入动态 GIF/WebP 作为纹理资产的空白。功能较为完整，支持编辑器导入和运行时加载，具有一定的实用价值，适用于需要动态纹理表现的 UI 或材质效果场景。

- [GASPALS](https://github.com/PolygonHive/GASPALS)  Integration of ALS Overlay Layering System into Unreal Engine 5 Game Animation Sample.
  - 该项目将高级运动系统（ALS）的覆盖层叠系统集成到 Unreal Engine 5 的游戏动画样本中。它提供了基于动画图和链接层的覆盖系统，允许通过简单的覆盖姿态改变整个运动动画，并包含基础武器附着系统和切换器。
  - 💬 项目基于 UE5 动画样本，集成了 ALS 的覆盖层叠系统，适合需要增强运动动画控制的开发者。提供详细的迁移指南，但作为完整插件，可能对新手有一定学习成本。
  🔗 [UE-Only Content - Licensed for Use Only with Unreal Engine-based Products](https://www.unrealengine.com/en-US/eula/content) · [Polygon Hive Discord](https://discord.gg/8KK5WnDp3D)

- [AnimToTextureHelpers](https://github.com/kromond/AnimToTextureHelpers)  Plugin for creating vertex animation textures in Unreal Engine.
  ![AnimToTextureHelpers screenshot](https://user-images.githubusercontent.com/5624947/211672718-688c375f-e9b9-4872-85d8-2ba624694084.png)
  - 💬 这是一个基于蓝图的 Unreal Engine 工具，用于将骨骼网格体动画转换为顶点动画纹理，适用于人群动画等性能优化场景。使用简便，但可能需要根据项目需求调整，示例性质较强。
  🔗 [Mann763](https://github.com/Mann763) · [tomaaron](https://github.com/tomaaron)



## Niagara
- [Niagara Destruction Driver](https://github.com/eanticev/niagara-destruction-driver) Turn CHAOS destructibles (Geometry Collection assets) into very performant GPU simulated destructible static meshes driven by Niagara particles.
  - 使用Niagara驱动chaos破坏的网格体，用GPU提高性能，非常好的学习资源
  - ![alt text](/libraries/images/00_image-21.webp)

- [SpawnToNiagara](https://github.com/aggressivemastery/SpawnToNiagara) This sample provides blueprint code and levels examples on how to spawn specific textured (selected by per particle random value) particles to a single niagara system.
  - 相关项目：https://github.com/aggressivemastery/NaniteMaterialUnification 演示如何使用 PerInstanceCustomData 和 CustomPrimititiveData 在单个主材质中驱动纹理选择。这使得 Nanite 网格及其上的所有材质能够通过一次DrawCall进行渲染。


  - GameDevMicah 是GiantessPlayground的作者：https://x.com/gamedevmicah



 



## Gameplay

- [HeartGraph](https://github.com/Drakynfly/HeartGraph) A generic runtime node graph editor and viewer for Unreal Engine. Supports versions 5.3 and 5.4, with legacy branch for 5.2 with a limited feature set. Compiles on Windows and macOS.
  - ![alt text](/libraries/images/00_image-1.webp)
  - 在运行时给玩家提供蓝图编辑器！


- [GameItemsPlugin](https://github.com/bohdon/GameItemsPlugin) An Unreal plugin with classes and tools for creating gameplay items, inventories and equipment.
  - Lyra 的扩展，GAS相关，MVVM，可以学习一下相关写法。


- [GameExperiencesPlugin](https://github.com/bohdon/GameExperiencesPlugin) An Unreal plugin for defining modular extensions to game modes that leverage the GameFeatures plugin. Based on Lyra experiences.
  - 一系列游戏功能操作，用于模块化添加技能、控件等。它与 GameExperiences 插件完美兼容，允许每个体验自定义要启用的技能和 UI。

- [ExtendedGameplayAbilitiesPlugin](https://github.com/bohdon/ExtendedGameplayAbilitiesPlugin) Unreal plugins that extend gameplay abilities and related systems.
  - GAS的一些扩展，可以参考学习一下

- [Starfire](https://github.com/MagForceSeven/Starfire) A collection of UE5 plugins that I've developed over the course of my hobby development. Some of which has also been used professionally in some version.
  

- [UE-Portals](https://github.com/rchaucha/UE-Portals) This plugin has been developed for the study of visual properties only. Thus, although the teleportation aspect has been implemented, it is really secondary and not much work has been put into it. Main branch works for UE-5.1 thanks to @dirtydanisreal, and there is a dedicated branch for UE-4.
  ![alt text](/libraries/images/00_image-65.webp)


- [Array-Utils](https://github.com/pyoneerC/Array-Utils) STL utilities for Unreal Engine Arrays.
  ![alt text](/libraries/images/00_image-64.webp)


- [SharedCoolingAbility](https://github.com/hbdjzwl/SharedCoolingAbility) SharedCoolingAbility是一款简洁式开箱即用支持单机、联机的共享冷却插件，不需要你写一行代码，也不会耦合你的项目代码，只需要在自己的AbilitySystemComponent类继承一个接口和继承自共享冷却Ability即可实现公共CD。不管你是项目使用还是插件使用都非常的便捷。
  ![alt text](/libraries/images/00_image-63.webp)


- [ue-gameplay-work-balancer](https://github.com/eanticev/ue-gameplay-work-balancer ) Unreal Engine Plugin that helps you spread work (time slice it) across multiple frames so your game maintains a stable frame rate (FPS).
  ![alt text](/libraries/images/00_image-22.webp)

- [VoxelPlugin](https://github.com/VoxelPlugin/VoxelCore) Open-source plugin with the Core module of Voxel Plugin
  - 虚幻引擎5的voxel插件 https://voxelplugin.com/
  - 个人免费使用，目前只开源了1.0，2.0预览版需要付费
  - ![alt text](/libraries/images/00_image-23.webp)


- [FutureExtensions](https://github.com/splash-damage/future-extensions) Unreal Engine plugin for async task programming




- [UE5Coro](https://github.com/landelare/ue5coro)UE5Coro 为虚幻引擎 5 实现了 C++20 协程支持，注重游戏逻辑、便利性，并提供与引擎的无缝集成。UE5Coro implements C++20 coroutine support for Unreal Engine 5 with a focus on gameplay logic, convenience, and providing seamless integration with the engine.
  - 让蓝图也支持协程函数。
  - wrap了多个module, 使用方便。
  - ```C++
        UFUNCTION(BlueprintCallable, meta = (Latent, LatentInfo = LatentInfo))
    FVoidCoroutine Example(FLatentActionInfo LatentInfo)
    {
        UE_LOGFMT(LogTemp, Display, "Before delay");
        co_await UE5Coro::Latent::Seconds(1); // Does not block the game thread!
        UE_LOGFMT(LogTemp, Display, "After delay");

        // Moving out of the game thread is as easy...
        co_await UE5Coro::Async::MoveToTask();
        UE_LOGFMT(LogTemp, Display, "In game thread: {0}", IsInGameThread());
        FString Value = TEXT("Imagine this was expensive to compute");

        // ...as moving back in:
        co_await UE5Coro::Async::MoveToGameThread();
        UE_LOGFMT(LogTemp, Display, "In game thread: {0}", IsInGameThread());
        UE_LOGFMT(LogTemp, Display, "Value: {0}", Value);
    }
    ```

- [GenericGraph](https://github.com/jinyuliao/GenericGraph) Generic graph data structure plugin for ue4
  ![alt text](/libraries/images/00_image-2.webp)
  - VoxelPlugin作者推荐的通用图数据结构插件

- [FlowGraph](https://github.com/MothCocoon/FlowGraph) 将其作为开源项目发布的目的是让人们能够更轻松地讲述精彩的故事并构建身临其境的世界。这使我们能够丰富视频游戏的故事叙述，从而激励人们并让我们的世界变得更美好。 Design-agnostic node system for scripting game’s flow in Unreal Engine
  - ![alt text](/libraries/images/00_image-24.webp)

- [Dialogue Plugin](https://github.com/NotYetGames/DlgSystem) Dialogue Plugin System for Unreal Engine

- [SPUD](https://github.com/sinbad/SPUD) 易用存档系统。 SPUD is a save game and streaming level persistence solution for Unreal Engine 5.
- [UE5-ApparatusECS-CrowdBattlePlugin](https://github.com/LeroyMackerl/UE5-ApparatusECS-CrowdBattlePlugin)  A crowd battle plugin for Unreal Engine based on Apparatus ECS.
  - 💬 插件基于 ECS 架构实现高性能群体战斗，支持大规模实体模拟，但处于测试阶段且依赖付费组件，适合有特定需求的 UE5 项目。


- [stream-chat-unreal](https://github.com/GetStream/stream-chat-unreal) 聊天框架，源码值得学习。该steam不是那个steam。The Stream Chat SDK is the official Unreal SDK for Stream Chat, a service for building chat and messaging games and applications.
  - ![alt text](/libraries/images/00_image-25.webp)

## Character

- [Mutable](https://github.com/anticto/Mutable-Documentation/wiki/Use-Cases) 角色自定义系统 Mutable generates skeletal meshes at runtime in your game. If your project needs content that can change dynamically, then Mutable is a good candidate to do that for you. It is always referred to as a "Character customization system", however it can generate any kind of skeletal mesh, including animls, props and weapons.
  - ![alt text](/libraries/images/00_image-26.webp)



## UI

- [Ultimate-CommonUI-Menu-System](https://github.com/Adriwin06/Ultimate-CommonUI-Menu-System) This project provide the Ultimate Modular Menu System for Unreal Engine 5 using Common UI where everything is easy to reuse/build on. For the options menu, there is everything you need from basic scalability settings to DLSS/FSR/XeSS/NIS/TSR settings but also Post Process or Lumen settings and NvRTX settings like RTXDI or SER.
  ![alt text](/libraries/images/00_image-3.webp)
  - 非常多功能，还有NVRTX分支的支持！支持Enhanced Input
  - TSR/DLSS/FSR/XeSS设置、音频/音量设置（音乐、环境音效、音效、语音、控制器扬声器等）、输入映射等等。


- [UMG3dRenderWidget](https://github.com/krojew/UMG3dRenderWidget) The UMG3dRenderWidget plugin provides the bridge between the PocketWorlds plugin from Epic (available in Lyra) and UE projects. This allows for adding 3d views of whole levels in a normal UMG widget.
 - Lyra的扩展，可以将3D场景渲染到UMG中
 - 这个插件 “UMG3dRenderWidget” 提供了一个桥梁，把 Epic 的 PocketWorlds 插件（通常用于 Lyra 框架中）与 UE 项目连接，使得可以在普通的 UMG 界面中显示整个关卡的 3D 视图
 - 如果你想在 UI 中展示 独立世界（比如角色选择界面、商店模型、迷你场景），UMG3dRenderWidget 这类插件更合适。
 - 如果你只是想把 主场景或子区域 渲染到 UI 上，RenderTarget 足够。

- [Game UI Assets Guide](https://github.com/miltoncandelero/game-ui-assets-guide) This is a guide for UI/UX artists and designers when they need to send their exported files to the programmers that need to implement them in games.
 - 给艺术家和设计师的UI 资产导出指南，方便和程序员沟通。


- [DeferredPainter](https://github.com/Sharundaar/DeferredPainter) An UMG exposed deferred paint container for Unreal.
  - 这个 Deferred Paint Container (延迟绘制容器) 的核心作用就是绕过这个常规的绘制流程。当 Defer render (延迟渲染) 被启用时，它会告诉渲染器：“先别画我里面的东西，等你们把其他所有常规的UI都画完了，最后再来画我。”
  



- https://github.com/DoubleDeez/MDFastBinding A versatile and performant alternative to UMG property bindings for designer-friendly workflows. The goal was to build a tool that allows mutating raw data into a form that can drive visuals, all within the editor, while staying performant.
  - 一个多功能且高效的 UMG 属性绑定替代方案，适用于设计师友好的工作流程。目标是构建一个工具，允许将原始数据转换为可驱动视觉效果的形式，所有操作都在编辑器内完成，同时保持高性能。
  - ![alt text](/libraries/images/00_image-72.webp)



- [UIDatasource](https://github.com/Sharundaar/UIDatasource) Light MVVM plugin for UI development
  - ![alt text](/libraries/images/00_image-71.webp)

- [CowNodes](https://github.com/sleepCOW/CowNodes) Improved Version of Epic's CreateWidget and CreateWidgetAsync (from CommonGame)
  - 异步创建widget

- [WidgetSplineSystem](https://github.com/ArmainAP/Unreal-Engine-Widget-Spline-System) Unreal-Engine-Widget-Spline-System is a free and open-source plugin for Unreal Engine that introduces a powerful spline widget. With this widget, developers can effortlessly draw 2D lines which can be edited both in the UMG editor and during runtime.
  - 可编辑的样条线绘制widget，发者可以轻松绘制 2D 线条，并且这些线条可以在 UMG 编辑器和运行时进行编辑

- [NiagaraUIRenderer](https://github.com/SourySK/NiagaraUIRenderer) Niagara UI Renderer | Free Plugin for Unreal Engine 
  - ![alt text](/libraries/images/00_image-27.webp)

- [MeshWidgetExample](https://github.com/dantreble/MeshWidgetExample) SMeshWidget Example

- [UINavigation](https://github.com/goncasmage1/UINavigation) 不想用CommonUI可以考虑这个。A UE4/5 plugin designed to help easily make UMG menus navigated by mouse, keyboard and gamepad

- [UE-BYGRichText](https://github.com/BraceYourselfGames/UE-BYGRichText) Rich text library supporting customizable Markdown formatting
  - | Feature | Unreal Rich Text | BYG Rich Text |
    | --- | --- | --- |
    | Nested styles					| :x:					| :heavy_check_mark:	|
    | Customizable syntax   		| :x:					| :heavy_check_mark:	|
    | Markdown-like shortcuts		| :x:					| :heavy_check_mark:	|
    | Inline images					| :heavy_check_mark:	| :heavy_check_mark:	|
    | Style-based justification		| :x: (block only)		| :heavy_check_mark:	|
    | Style-base margins			| :x: (block only)		| :heavy_check_mark:	|
    | Inline tooltips				| :heavy_check_mark:	| :heavy_check_mark:	|
    | Customizable paragraph separator | :x: | :heavy_check_mark:					|
    | XML-like syntax   			| :heavy_check_mark:	| :heavy_check_mark:	|
    | Datatable-based stylesheet	| :heavy_check_mark:	| :x:					|
    | Blueprint code support		| :heavy_check_mark:	| :x:					|

- [ElementUI-UMG-Kit](https://github.com/rdelian/ElementUI-UMG-Kit) An easy way to change the style of your elements that extends beyond the default ones the Common UI provides.
  - ![alt text](/libraries/images/00_image-28.webp)

- [UI Tweening Libary for UE4/UMG](https://github.com/benui-dev/UE-BUITween) UI 补间动画方便C++ 使用。 Unreal 4 UMG UI tweening plugin in C++
  ```C++
    // Make UWidget MyWidget fade in from the left
    const float TweenDuration = 0.7f;
    const float StartDelay = 0.3f;
    UBUITween::Create( MyWidget, TweenDuration, StartDelay )
      .FromTranslation( FVector2D( -100, 0 ) )
      .FromOpacity( 0.2f )
      .ToReset()
      .Easing( EBUIEasingType::OutCubic )
      .Begin();
  ```

- [UEImgui](https://github.com/ZhuRong-HomoStation/UEImgui) IMGUI的使用，支持代码编辑器
  ![alt text](/libraries/images/00_image-29.webp)

- [运行时图片加载器](https://github.com/RaiaN/RuntimeImageLoader) 支持GIF，webp 格式。 Load images and GIFs into Unreal at runtime without hitches
  ![alt text](/libraries/images/00_image-30.webp)
- [VirtualFlowLayout](https://github.com/MikeShatterwell/VirtualFlowLayout)  A virtualized scrollable list widget for Unreal Engine 5.
  ![VirtualFlowLayout screenshot](https://raw.githubusercontent.com/MikeShatterwell/VirtualFlowLayout/main/Docs/main.gif)
  - 💬 这是一个功能全面的 UE5 UI 插件，专注于虚拟化滚动列表布局，支持层次结构和多种布局引擎，适合处理复杂列表场景，但项目 stars 数较低，社区关注度有限，需评估其稳定性和维护状态。
  🔗 [InputFlowDebugger](https://github.com/MikeShatterwell/InputFlowDebugger)

- [DreamUMG](https://github.com/TypeDreamMoon/DreamUMG)  A plugin extending Unreal Engine UMG/Slate with text animations and pseudo-3D transforms.
  - 一个为 Unreal Engine 的 UMG/Slate UI 框架设计的扩展插件。它主要提供动态文本动画、在2D UI中实现伪3D透视效果以及可由蓝图动态组装的UI树结构等功能。
  - 💬 一个功能聚焦的UE插件，文档详尽，为UMG/Slate提供了文本动画和2D伪3D变换等常用视觉增强。其Stars数表明社区关注度有限，更适合作为特定UI效果的工具库集成到项目中。



## Material

- [MaterialVault](https://github.com/ScottRaffertyCG/MaterialVault) The purpose of this plugin is to provide a consolidated and comprehensive interface for all types of projects to work with. Any projects needing materials and textures can use this interface much faster and efficently than the standard spread out functions native to Unreal. Save time on set or in studio by not needing to navigate through folders and getting lost. Quickly see, Apply and Edit materials directly in this interface. Version control of materials in Lookdev, CMF and other sub functions of an industry can utilize this interface to have a much more hands on and instant feedback and adapt system within Unreal.

- [Automotive Materials](https://www.fab.com/listings/5dd132fe-ee32-4e8c-9cd3-7496547dfb29) Automotive Materials is a collection of 164 high quality automotive-themed Materials and Textures which have been setup for use in Unreal Engine 4. The materials have been optimized to take advantage of techniques and features such as ray tracing and object space triplanar projection.



- [Unreal_Engine_Essential_Materials_UE5](https://github.com/motionforge/Unreal_Engine_Essential_Materials_UE5) This Unreal Engine Project contains a selection of Materials and Material Functions that can be used for most if not all surfaces.
  ![alt text](/libraries/images/00_image.webp)
  - 一个精选的UE5材质库，包含基础模板（如视差遮挡、布料动画和主材质），所有纹理使用Creative Commons许可。文件大小优化，适合快速导入项目



- [CompushadyUnreal](https://github.com/rdeioris/CompushadyUnreal) Compushady is an Unreal Engine 5 plugin aimed at easily (and quickly) executing GPU shaders.
  ![alt text](/libraries/images/00_image.png)
  - 简化HLSL绑定, 更容易使用的Compute Shader for UE5
  - 支持 GLSL, HLSL, 直接在蓝图使用，自带高亮



- [RTMSDF](https://github.com/rtm223/RTMSDF) 2D signed distance field generators & importers for Unreal Engine 5
  ![alt text](/libraries/images/00_image-81.webp)
  - An Unreal Engine 5 Plugin that provides importers for generating 2D SDFs from .svg source files and all Unreal-supported texture source files (.psd, .png, .tif etc). Uses MSDFGen for processing of SVG files. Currently supports UE5.4+





- [SceneViewExtensionTemplate](https://github.com/A57R4L/SceneViewExtensionTemplate)Unreal Engine 5 plugin template for adding a custom rending pass into the engine with a SceneViewExtension
  - 为 Unreal Engine 5 提供的插件模板，目的是在不改引擎源码的前提下，向渲染管线里注入自定义渲染 pass（custom rendering pass），通过 Unreal 的 SceneViewExtension 接口 + 引擎子系统（Engine Subsystem）维持生命周期。 
  - 


- [UE5_Tut_5_Custom_Material_Node](https://github.com/RyanSweeney987/UE5_Tut_5_Custom_Material_Node) Tutorial code for how you can create your own material nodes for use in any material. The example is a simple Desaturate node.



- [MaterialMaker](https://github.com/RodZill4/material-maker) A procedural textures authoring and 3D model painting tool based on the Godot game engine
  - 虽然说支持 Unreal Engine，但是测试发现生成的hlsl 依然代码存在很多报错 (2025.7.30)
  - ![alt text](/libraries/images/00_image-58.webp)


- [ProceduralDrawingMaterialSamples](https://github.com/EmbarrassingMoment/ProceduralDrawingMaterialSamples ) About
A collection of procedural drawing material samples for Unreal Engine (UE5). Useful for learning technical art and for reference in your projects.
  - ![alt text](https://github.com/EmbarrassingMoment/ProceduralDrawingMaterialSamples/raw/master/gif/Snow.gif)
  - ![alt text](https://github.com/EmbarrassingMoment/ProceduralDrawingMaterialSamples/raw/master/gif/Animation.gif)

- [DarknessFX/UEMaterials](https://github.com/DarknessFX/UEMaterials ) DarknessFX Collection of Unreal Engine Materials
  ![alt text](/libraries/images/00_image-32.webp)


- [DreamShader](https://github.com/TypeDreamMoon/DreamShader)  Unreal Engine Material DSL for generating materials via text-based language.
  - DreamShader 是一个基于 DSL 的 Unreal Engine 材质生成工具，通过文本化方式简化材质创建流程，近年来文本化工作流广受欢迎，有效解决了手动连节点的痛点。
  - 💬 该项目通过 DSL 文本化材质生成，提升了开发效率，但作为新工具，生态和稳定性可能需要时间验证。

- [Texture Sets](https://github.com/electronicarts/texturesets)  A UE5 plugin providing an opt-in framework for advanced, streamlined texture pipelines.
  ![Texture Sets screenshot](https://raw.githubusercontent.com/electronicarts/texturesets/main/Docs/Img/tiltshift_textureset_01.png)
  - Texture Sets 是由 EA 的 SEED 团队为 Unreal Engine 5 开发的插件，提供了一个可选框架，用于构建高级、精简的纹理管线。它简化了纹理打包和材质设置，提升了工作流程的标准化和优化。
  - 💬 该项目由 EA 专业团队开发，专注于 UE5 纹理管线优化，适合中大型项目提升美术工作流效率。但作为框架，可能需要额外配置和学习。
  🔗 [Martin Palko](https://www.martinpalko.com/) · [EA Motive](https://www.ea.com/ea-studios/motive) · [SEED](https://www.ea.com/seed)

- [TextureChannelPacker](https://github.com/EmbarrassingMoment/RGBPackingTool)  An Unreal Engine plugin for packing grayscale textures into RGBA channels.
  ![TextureChannelPacker screenshot](https://raw.githubusercontent.com/EmbarrassingMoment/RGBPackingTool/main/Docs/Images/ui_overview.png)
  - 一个用于UE5的纹理通道打包工具，能够自动调整输入纹理尺寸并将其打包到单个RGBA资产中，优化了纹理加载与性能。
  - 💬 功能聚焦的UE插件，解决了游戏中常见的ORM纹理打包需求，自动化程度高，但作为‘简单工具’可能功能深度有限。
  🔗 [**Get it on Fab**](https://www.fab.com/listings/7b231ecc-079f-45dc-9b8e-45dacc6b0771)

- [Urban Myth Post Process](https://github.com/n-ln/ue-urban-myth-pp)  An Unreal Engine post process effect inspired by Urban Myth Dissolution Center.
  - 这是一个 Unreal Engine 后处理效果插件，灵感来源于游戏《都市传说解体中心》。提供了明亮和暗场景的示例关卡，适用于 UE 5.3 及以上版本。
  - 💬 项目结构清晰，提供了详细的使用说明和兼容性信息，适合学习或应用自定义后处理效果，但功能较为基础，可能需进一步扩展。
  🔗 [Urban Myth Dissolution Center (『都市伝説解体センター』)](https://umdc.shueisha-games.com/) · [Link to blog](https://zenn.dev/nlnnn/articles/2c33ea89605559)



## NetWork

- [UE5.5-SteamSessionHelper](https://github.com/Sohel160202/UE5.5-SteamSessionHelper) Blueprint-friendly fix for Steam hosting/joining issues in Unreal Engine 5.5.
  ![alt text](/libraries/images/00_image-85.webp)
  - Unreal Engine 5.5 在 OnlineSubsystemSteam 中引入了一些怪癖，破坏了多人游戏的工作流程，👉 此插件修复了这些问题并恢复了可靠的 Steam 多人游戏工作流程。



- [VaRest](https://github.com/ufna/VaRest) REST API plugin for Unreal Engine 4 - we love restfull backend and JSON communications!
  - 该项目作者已经停止维护， 作者推荐自己fork后使用。
  - 但fab 版本依然在更新，且免费：https://www.fab.com/listings/5b751595-fe3e-4e85-b217-9b5496ab6d3f
- [TurboLink](https://github.com/thejinchao/turbolink)  An Unreal Engine plugin for integrating Google gRPC with C++ and Blueprint.
  ![TurboLink screenshot](https://github.com/thejinchao/turbolink/wiki/image/TurboLink.png)
  ![TurboLink screenshot](https://github.com/thejinchao/turbolink/wiki/image/turbolink_example.png)
  ![TurboLink screenshot](https://github.com/thejinchao/turbolink/wiki/image/project-config.png)
  - TurboLink 是一个 Unreal Engine 插件，允许使用 C++ 和 Blueprint 将 Google gRPC 集成到 Unreal Engine 中。它支持跨平台、异步调用、流式 gRPC 等功能，适用于需要高效网络通信的项目。
  - 💬 项目专注于 Unreal Engine 与 gRPC 的集成，提供了 Blueprint 支持和跨平台兼容性，适合需要在 UE 项目中实现复杂网络通信的开发者。但需注意 gRPC 的复杂性可能对新手不友好。
  🔗 [Google gRPC](https://grpc.io/) · [Unreal Engine](https://www.unrealengine.com/) · [protoc-plugin code generation tool](https://github.com/thejinchao/protoc-gen-turbolink)

- [EOS Getting Started Guide](https://github.com/EpicGames/EOS-Getting-Started)  Guide and code samples for integrating Epic Online Services (EOS) with Unreal Engine and C#.
  - 💬 由Epic Games官方维护的入门教程与示例代码库，覆盖了EOS在UE中的核心功能集成。代码组织清晰，以教学为目的，适合开发者学习网络功能的快速实现，但部分示例代码可能较为基础。
  🔗 [Epic Online Services blog](https://dev.epicgames.com/news) · [Epic Developer Community](https://dev.epicgames.com/community/) · [Introduction to Epic Online Services (EOS)](https://dev.epicgames.com/news/introduction-to-epic-online-services-eos#series-reference)



## Framework

- [PCGExtendedToolkit](https://github.com/Nebukam/PCGExtendedToolkit) PCGEx is a free (libre) Unreal 5 plugin that expands PCG capabilities. It offers a variety of high-performance nodes; with an edge for building relational graphs (Freeform, Delaunay, Voronoi, MST etc), advanced pathfinding; and much more.
  - 比官方PCG更强大的PCG工具，带示例项目：https://github.com/Nebukam/PCGExExampleProject
  - 文档 https://nebukam.github.io/PCGExtendedToolkit/
  - ![alt text](/libraries/images/00_image-33.webp)

- [imgui](https://github.com/ocornut/imgui) 代码驱动的UI开发方式，无需可视化编辑器, 对程序员非常友好。 Dear ImGui: Bloat-free Graphical User interface for C++ with minimal dependencies
  - API简单直观，学习曲线平缓
  - 快速实现工具类UI，如调试面板、属性编辑器等
  - 非常适合做游戏内调试工具、编辑器扩展
  - ![alt text](/libraries/images/00_image-34.webp)

- [Taichi](https://github.com/taichi-dev/taichi) Taichi 是一个并行计算框架，适合计算密集型任务（例如写Shader、物理仿真和人工智能等任务）高度依托于并行计算 Productive, portable, and performant GPU programming in Python.
  - [相似框架对比](https://forum.taichi-lang.cn/t/topic/2621) 
  - Taichi Lang 提供了一组称为SNode (/ˈsnoʊd/) 的通用数据容器，这是一种组合分层、多维字段的有效机制。这可以涵盖数值模拟中的许多使用模式（例如空间稀疏计算）。
  - cgerchenhp表示将 Taichi 集成到虚幻引擎中非常容易。充分利用 Taichi 的高性能并行计算和 UE 对 Python 的支持（通过插件 [TAPython](https://github.com/cgerchenhp/TAPython_Taichi_StableFluid_UE5)）
  - ![alt text](/libraries/images/00_image-35.webp)



- [spine-runtimes](https://github.com/EsotericSoftware/spine-runtimes) Spine 是一款针对游戏开发的 2D 骨骼动画编辑工具, 支持虚幻。

- [MassSample](https://github.com/Megafunk/MassSample) understanding of Unreal Engine 5's experimental ECS plugin with a small sample project.
  - ![alt text](/libraries/images/00_image-36.webp)

- [MassAIExample](https://github.com/Ji-Rath/MassAIExample) A project primarily used to experiment with Mass, an ECS Framework
  - ![alt text](/libraries/images/00_image-37.webp)
  - ![alt text](/libraries/images/00_image-38.webp)

- [MaaassParticle](https://github.com/DevDingDangDong/MaaassParticle.git) A UE5 plugin that renders large-scale crowds through Niagara and can control them via state management. This is the Epic project deliverable from Krafton Game Tech Lab 1st Generation Team 2.
  ![alt text](/libraries/images/00_image-39.webp)

- [OmegaGameFramework](https://github.com/StudioSyndiCatCaius/OmegaGameFramework)  A free, open-source high-level plugin for Unreal Engine that streamlines game development with many common features out of the box.
  ![OmegaGameFramework screenshot](https://raw.githubusercontent.com/StudioSyndiCatCaius/OmegaGameFramework/main/docs/images/Screenshots/OGF_0.png)
  ![OmegaGameFramework screenshot](https://raw.githubusercontent.com/StudioSyndiCatCaius/OmegaGameFramework/main/docs/images/Screenshots/OGF_1_abilities.png)
  ![OmegaGameFramework screenshot](https://raw.githubusercontent.com/StudioSyndiCatCaius/OmegaGameFramework/main/docs/images/Screenshots/OGF_2_attributes.png)
  - 💬 这是一个面向 Unreal Engine 开发者的大型游戏框架插件，集成了能力、属性、模块化系统等常见玩法系统，旨在简化开发流程、快速构建原型，适合希望避免重复造轮子的团队或个人开发者。
  🔗 [Website](https://www.studiosyndicat.com/omegagameframework) · [Unreal Engine Marketplace](https://www.unrealengine.com/marketplace/en-US/product/2ca6202e55f44cfd82659fbca6591603) · [Subreddit: Discussion & Support](https://www.reddit.com/r/OmegaGameFramework/)

- [MassAPI](https://github.com/LeroyMackerl/MassAPI)  User friendly C++ and Blueprint API for Unreal Engine's Mass Entity system.
  - MassAPI 是一个为 Unreal Engine 的 Mass Entity 框架设计的开源插件，提供了用户友好的 C++ 和蓝图接口。它简化了 Mass Entity 系统的使用，支持动态标志系统和延迟操作，并兼容 UE5.6 及以上版本。
  - 💬 该项目通过封装 Mass Entity 的复杂 API，降低了使用门槛，但文档由 AI 生成可能存在错误，适合需要快速集成 Mass Entity 功能的开发者。


- [UnrealLibretro](https://github.com/N7Alpha/UnrealLibretro) Libretro 游戏模拟器 UnrealLibretro is a Libretro Frontend for Unreal Engine. It is a Blueprint compatible library that lets you run emulators within Unreal Engine. More Technically it allows you to run Libretro Cores.
  - https://github.com/libretro/RetroArch
  - ![alt text](/libraries/images/00_image-40.webp)

## Tools

- [UnrealEngine-UpdateTracker](https://github.com/pafuhana1213/UnrealEngine-UpdateTracker) This project is an automated service that periodically monitors updates to Unreal Engine's private GitHub repository, summarizes important changes (such as new features and specification changes) using AI (Google Gemini), and posts them as reports to GitHub Discussions.
  - 使用 Gemini AI 自动化分析 Unreal Engine 的更新，生成的报告将作为“虚幻引擎每日报告”发布到存储库的 GitHub 讨论中



- https://github.com/Buckminsterfullerene02/UE-Modding-Tools A databank of every UE modding tool & guide that have potential to be used across multiple UE games
  - 这是一个涵盖所有可能适用于多款虚幻引擎游戏的模组工具的数据库。


- [UETools-GUI](https://github.com/Cranch-fur/UETools-GUI) Dumper-7 (SDK) based solution for rapid debugging of Unreal Engine powered titles.
  - 一个基于 Dumper-7 的运行时调试 / modding 工具。作者在 README 里写明用于快速调试并且提到用 DLL 注入到游戏进程，还列出 Cheat Engine 等注入工具作示例


- [UnrealAnalyzerMCP](https://github.com/ayeletstudioindia/unreal-analyzer-mcp) A Model Context Protocol (MCP) server that provides powerful source code analysis capabilities for Unreal Engine codebases. This tool enables AI assistants like Claude and Cline to deeply understand and analyze Unreal Engine source code.



- [DreamTranslatePO](https://github.com/TypeDreamMoon/DreamTranslatePO) An automated translation tool for po localization files or csv localization files
  - 虚幻引擎本地化工具，支持PO文件和CSV文件的自动翻译 接入AI
  ![alt text](/libraries/images/00_image-66.webp)


- [UnrealHeightMap](https://github.com/manticorp/unrealheightmap) Unreal Engine 16 Bit Grayscale PNG Heightmap Generator
  - 在线高度图生成工具，经测试，大部分真实地形都能获取；少部分区域只能获取低精度。
  - https://manticorp.github.io/unrealheightmap/



- [DreamUnrealManager](https://github.com/TypeDreamMoon/DreamUnrealManager) WinUI3 Unreal Engine Project / Unreal Engine Manager
  - UE引擎/项目管理器 + 可视化预编译插件批量构建工具
  ![alt text](/libraries/images/00_image-55.webp)



- [KeywordGacha](https://github.com/neavo/KeywordGacha) 使用 AI 能力分析 小说、游戏、字幕 等文本内容并生成术语表的次世代翻译辅助工具
  ![alt text](/libraries/images/00_image-41.webp)


- [ComfyTextures](https://github.com/AlexanderDzhoganov/ComfyTextures) 用扩散模型给3d模型场景自动生成贴图。 Unreal Engine ⚔️ ComfyUI - Automatic texturing using generative diffusion models
  ![alt text](/libraries/images/00_image-42.webp)

- [RGB↔X](https://github.com/zheng95z/rgbx) AI根据输入图片生成材质。 RGB↔X: Image Decomposition and Synthesis Using Material- and Lighting-aware Diffusion Models
  ![alt text](/libraries/images/00_image-43.webp)

 - [Libretro Shader](https://github.com/libretro/glsl-shaders) 老电视机、老游戏 滤镜。 This repo is for glsl shaders converted by hand from libretro's common-shaders repo, since some don't play nicely with the cg2glsl script.
  ![alt text](/libraries/images/00_image-44.webp)

- [glslViewer](https://github.com/patriciogonzalezvivo/glslViewer) Console-based GLSL Sandbox for 2D/3D shaders
  ![alt text](https://github.com/patriciogonzalezvivo/glslViewer/raw/main/.github/images/03.gif)
- [UnrealPakViewer](https://github.com/jashking/UnrealPakViewer)  A graphical tool for viewing UE4 Pak files, supporting pak and ucas files.
  ![UnrealPakViewer screenshot](https://raw.githubusercontent.com/jashking/UnrealPakViewer/master/Resources/Images/OpenPak.png)
  ![UnrealPakViewer screenshot](https://raw.githubusercontent.com/jashking/UnrealPakViewer/master/Resources/Images/AESKey.png)
  ![UnrealPakViewer screenshot](https://raw.githubusercontent.com/jashking/UnrealPakViewer/master/Resources/Images/PakSummary.png)
  - 一个用于可视化查看 UE4 Pak 文件的图形化工具，支持 UE4 pak 和 ucas 文件格式，提供树形视图、列表视图和详细资源分析功能。
  - 💬 该项目功能全面，支持多线程解压、资源注册表加载和加密处理，适用于 UE4 开发者管理和分析打包资源；Stars 数较高，表明社区认可度不错。

- [Unreal Package Manager](https://github.com/jackcayc924/UnrealPackageManager)  An npm-style package manager for Unreal Engine with dependency management and lockfiles.
  - 这是一个为 Unreal Engine 设计的 npm 风格包管理器，支持从 Git 仓库、本地文件夹或私有注册表安装包。它通过锁文件管理依赖项，确保团队构建的一致性，并可集成现有插件如 Fab 市场资产。
  - 💬 该项目提供了 UE 生态中稀缺的包管理工具，支持多种源和依赖解析，适合团队协作开发。但仅限 Windows 平台，且作为新兴工具，生态成熟度有待观察。
  🔗 [Verdaccio](https://verdaccio.org/) · [Nexus](https://www.sonatype.com/products/sonatype-nexus-repository)

- [PSOCacheBuster](https://github.com/Flassari/PSOCacheBuster)  Clears the PSO driver cache for non-shipping and non-editor builds for easier testing and profiling of first-run-like experience.
  - 💬 一个非常聚焦的小工具，解决了UE项目中测试‘首次运行’体验时因PSO缓存而导致性能数据不准确的特定痛点。项目结构清晰，功能单一，适合有相关需求的开发者。
  🔗 [The Unlicense](https://unlicense.org/)


- [UnrealGPUSwarm](https://github.com/timdecode/UnrealGPUSwarm) 学习compute shaders的例子。 This project is a good starting point for learning how to write compute shaders in Unreal. It implements a boid simulation the GPU. It achieves 0.5 million boids at 45 fps on a GTX 1080.
  <video src="https://user-images.githubusercontent.com/980432/132757577-500416e4-5f27-4add-9c50-641889336d69.mp4" controls autoplay loop> 
    Your browser does not support the video tag.
  </video>

## Plugins
- [TransitionFX_Dev](https://github.com/EmbarrassingMoment/TransitionFX_Dev) Unreal Engine 5 plugin providing various screen transition effects (Fade, Iris, Pixelate, etc.)
  ![alt text](https://raw.githubusercontent.com/EmbarrassingMoment/TransitionFX_Dev/master/docs/images/header.png)
  - TransitionFX 是一个轻量级的、基于 SDF 的程序化过渡插件，**完全不需要纹理**。一切都在蓝图中运行，设置只需几分钟，而且完全免费。
  - [fab](https://www.fab.com/listings/82f9a51f-52e6-4a01-a637-43a4dac76c0a)
  - [详情](https://x.com/endwar1338/status/2039352214150599001)


- [UnrealRoboticsLab](https://github.com/URLab-Sim/UnrealRoboticsLab) A high-fidelity, open-source robotics simulator integrating Unreal Engine's photorealistic rendering with MuJoCo's precision physics.
  - 把 MuJoCo 物理引擎嵌入 UE5，支持照片级渲染 + 精确物理接触、40+ 传感器、Python/ROS 2 集成、拖拽 MJCF 文件。适合机器人仿真、AI 训练

- [RTXGI-UE-5.7-Plugin](https://github.com/kpitikaris/RTXGI-UE-5.7-Plugin) Porting RTXGI to 5.7 and SM6
  - UE 5.7 专用的 RTX Global Illumination 插件（原版有 artifact 问题，这个 fork 修复了）。为了让尽可能多的开发者享受到 RTXGI 的优势，所有 RTXGI 1.1 的功能现在都可以通过 RTXGI UE 插件在虚幻引擎中使用。

- [Monolith](https://github.com/tumourlove/monolith)  An Unreal Engine 5.7+ plugin that provides AI assistants with full read/write access via MCP.
  - 这是一个 Unreal Engine 5.7 的 MCP 插件，为 AI 助手提供对蓝图、材质、Niagara VFX、动画、网格、AI（行为树/状态树/EQS/智能对象）、GAS、逻辑驱动器、ComboGraph、UI、音频（Sound Cues 和 MetaSounds）等的完全读写访问。包含 1,226 个操作，跨 16 个模块，零 Python 依赖。
  - 💬 项目功能全面，覆盖 UE 多个核心领域，通过 MCP 协议实现 AI 集成，适合需要自动化或 AI 辅助开发的 UE 项目，但作为大型插件可能需要一定学习成本。

- [MarkdownAssetProject](https://github.com/EmbarrassingMoment/MarkdownAssetProject)  An Unreal Engine 5.5+ plugin that adds a custom Markdown asset type with a live-preview editor.
  - 这是一个 Unreal Engine 5 插件，用于原生 Markdown 资产，提供实时 HTML 预览编辑器和蓝图访问功能。
  - 💬 该插件功能全面，集成 md4c 库支持实时预览和多种 Markdown 扩展，适合在 UE 项目中集成文档编辑功能，但仅限 Windows 平台。

- [PiUE](https://github.com/Solessfir/PiUE)  Blender-style radial quick-action menu for the Unreal Engine level editor viewport.
  ![PiUE screenshot](https://raw.githubusercontent.com/Solessfir/PiUE/main/Resources/Screenshot.png)
  - 💬 这是一个为 Unreal Editor 设计的 Blender 风格饼图菜单插件，提供了快速操作功能，可能提升编辑器工作效率。但项目关注度较低，需注意兼容性和维护状态。

- [Starfire](https://github.com/MagForceSeven/Starfire)  A collection of UE5 plugins for hobby game development.
  - 这是一个用于个人业余游戏开发的 UE5 插件集合，包含多个实用工具和系统，如资产管理和消息总线，旨在扩展引擎功能。
  - 💬 项目模块化设计清晰，提供了丰富的 UE5 插件功能，适合需要自定义工具和系统的开发者，但使用可能需要一定的引擎知识基础。
  🔗 [here](https://open.codecks.io/starfire)

- [glTFRuntime](https://github.com/rdeioris/glTFRuntime)  Unreal Engine Plugin for loading glTF files at runtime
  ![glTFRuntime screenshot](https://raw.githubusercontent.com/rdeioris/glTFRuntime-docs/master/Epic_MegaGrants_Recipient_logo_horizontal_black.png?raw=true#gh-light-mode-only "Megagrant")
  ![glTFRuntime screenshot](https://raw.githubusercontent.com/rdeioris/glTFRuntime-docs/master/Epic_MegaGrants_Recipient_logo_horizontal_white.png?raw=true#gh-dark-mode-only "Megagrant")
  - 💬 这是一个成熟的 Unreal Engine 插件，专注于运行时加载 glTF 文件，支持多种扩展格式和版本，适用于需要动态资产加载的游戏开发场景。
  🔗 [our Discord Channel](https://discord.gg/DzS7MHy) · [Instructions](https://github.com/rdeioris/gltfruntime-docs#notes-when-packaging-a-game) · [buy glTFRuntime](https://www.unrealengine.com/marketplace/en-US/product/gltfruntime)

- [ProceduralContentProcessor](https://github.com/Italink/ProceduralContentProcessor)  Unreal Engine Plugin providing procedural methods to manage objects, assets, and worlds.
  ![ProceduralContentProcessor screenshot](https://raw.githubusercontent.com/Italink/ProceduralContentProcessor/main/Resources/pcg-graph-editor.png)
  ![ProceduralContentProcessor screenshot](https://raw.githubusercontent.com/Italink/ProceduralContentProcessor/main/Resources/image-20240205111218033-1741055387931-5.png)
  ![ProceduralContentProcessor screenshot](https://raw.githubusercontent.com/Italink/ProceduralContentProcessor/main/Resources/f94d82fa-2f03-4cd2-9f0c-db710c6a91cb.png)
  - 这是一个 Unreal Engine 插件，提供程序化方法来管理对象、资产和世界。它旨在通过程序化技术提升游戏内容生产的效率和质量，适用于 Unreal Engine 5 开发。
  - 💬 项目专注于 UE5 的程序化内容管理，集成了多种程序化工具，适合技术美术师和开发者进行自动化内容生成，但代码质量和实际效果需结合具体实现评估。
  🔗 [程序化（Procedural）](https://en.wikipedia.org/wiki/Procedural_generation) · [**程序化内容生成**](https://docs.unrealengine.com/5.2/en-US/procedural-content-generation-overview/) · [**程序化建模**](https://en.wikipedia.org/wiki/Procedural_modeling)

- [PulldownBuilder](https://github.com/Naotsun19B/PulldownBuilder)  Easily create pull-down menus from data tables or string tables in Unreal Engine.
  ![PulldownBuilder screenshot](https://user-images.githubusercontent.com/51815450/173223798-f60374a1-1d14-4ac2-93c1-bdbab9fe5278.PNG)
  ![PulldownBuilder screenshot](https://user-images.githubusercontent.com/51815450/173223818-c8297c9c-6a0d-4e4a-938d-a15f55df9c49.PNG)
  ![PulldownBuilder screenshot](https://user-images.githubusercontent.com/51815450/173223842-a5356544-b7ee-4979-9864-36986ee358ec.PNG)
  - 该插件通过创建 PulldownContents 资产，可以轻松添加基于数据表、字符串表等显示下拉菜单的结构。适用于 Unreal Engine 4.27 至 5.7 版本，支持多平台，简化了编辑器中下拉菜单的创建流程。
  - 💬 这是一个针对 Unreal Engine 的编辑器插件，功能聚焦且实用，适合需要数据驱动下拉菜单的 UI 开发场景，但插件较为专用，通用性有限。
  🔗 [marketplace](https://www.unrealengine.com/marketplace/en-US/product/pulldown-builder) · [MIT License](https://en.wikipedia.org/wiki/MIT_License) · [Fab Standard License (Fab EULA)](https://www.fab.com/eula)

- [HotPatcher](https://github.com/hxhb/HotPatcher)  Unreal Engine hot update manage and package plugin.
  ![HotPatcher screenshot](https://img.imzlp.com/imgs/zlp/picgo/2021/20220526194731.png)
  - HotPatcher 是一个专注于虚幻引擎热更新管理、资源打包和包体优化的插件，支持从 UE4.21 到 UE5 的全平台开发。它提供了版本控制、差异打包、命令行集成等功能，简化了热更新流程。
  - 💬 项目成熟度高，功能全面且文档完善，适用于需要高效热更新方案的 Unreal Engine 项目，但作为工具插件，可能需要一定的学习成本。
  🔗 [UE资源热更打包工具HotPatcher](https://imzlp.com/posts/17590/) · [UE4热更新：HotPatcher插件使用教程](https://www.bilibili.com/video/BV1Tz4y197tR/) · [Unreal Open Day2022 UE热更新的原理与实现 | 查利鹏](https://www.bilibili.com/video/BV1d841187Pt/?zw)

- [UE5_NvidiaAnsel](https://github.com/MonsterGuo/UE5_NvidiaAnsel)  An Unreal Engine 5 plugin for Nvidia Ansel capture.
  ![UE5_NvidiaAnsel screenshot](https://github.com/MonsterGuo/UE5_NvidiaAnsel/assets/39860733/303d32df-57e9-492a-a3e2-a93c438cc1b6)
  ![UE5_NvidiaAnsel screenshot](https://user-images.githubusercontent.com/39860733/159846088-18804c78-c19a-47ca-8edc-ea44e3d7a3af.png)
  ![UE5_NvidiaAnsel screenshot](https://user-images.githubusercontent.com/39860733/159846137-8b6e1ee7-57e3-4cb8-b1bb-c78f52e559b2.png)
  - 这是一个将 Unreal Engine 4.27 的 Nvidia Ansel 插件移植到 UE5 的项目，支持 UE5.0 到 5.7 版本，提供普通和自动抓取两种模式，用于生成 360 度或立体 360 度影片。
  - 💬 该项目为 UE5 开发者提供了便捷的 Nvidia Ansel 集成，适合需要高分辨率截图和 360 度视频的场景，但依赖特定驱动版本，使用前需配置环境。

- [JsonAsAsset](https://github.com/JsonAsAsset/JsonAsAsset)  A powerful Unreal Engine plugin that imports assets from FModel using JSON files.
  - 一个功能强大的 Unreal Engine 插件，专门用于从 FModel 导入资产，支持材质、数据表和物理资产等多种类型，简化游戏资产移植工作流。
  - 💬 项目聚焦于资产导入的逆向工程，实用性强，适合模组制作者和需要批量处理游戏资产的开发者，但依赖 FModel 工具，使用范围相对专业。
  🔗 [Unreal Engine](https://www.unrealengine.com/en-US) · [JSON](https://www.json.org/json-en.html) · [(UEParse)](https://github.com/FabianFG/CUE4Parse)

- [RemRanges](https://github.com/RemRemRemRe/RemRanges)  A plugin bringing transrangers to Unreal Engine for efficient range transformations.
  - 该插件将 transrangers 引入 Unreal Engine，基于回调（push-based）设计模式优化范围变换性能，避免了传统 pull-based 方法中冗余的范围检查。
  - 💬 这是一个将外部 C++ 库移植为 Unreal Engine 插件的轻量级项目，专注于通过回调机制提升范围操作效率，适合性能敏感场景，但知名度较低。
  🔗 [transrangers](https://github.com/joaquintides/transrangers)

- [SimpleQuest](https://github.com/TheGeebus/SimpleQuest)  Goal state management authored in an intuitive visual graph for any Unreal Engine game.
  ![SimpleQuest screenshot](https://github.com/user-attachments/assets/9cc8e4f9-ee60-46fc-881a-5c45e38ff9d4)
  - 用于Unreal Engine 5.6的可视化图形化任务系统插件，支持设计师通过节点图进行非线性任务设计，具备嵌套前提表达式、命名结果、实时检查和诊断等高级功能。
  - 💬 一个功能相当完整且设计思路清晰的任务系统插件，其可视化编辑器和实时调试功能是亮点，适合中大型项目采用，但作为插件集成时需评估与项目自身任务系统的融合成本。
  🔗 [Simple Quest Discord server](https://discord.gg/PN9kzPypeS)

- [Viewport Manager](https://github.com/jackcayc924/ViewportManager)  Professional viewport management system for Unreal Engine 5.7+
  - 这是一个基于 C++ 的 Unreal Engine 插件，专为突破引擎默认的 4 玩家分屏限制而设计，支持创建多达 32 个可自定义视口。插件提供了完整的相机系统和布局工具，方便开发者实现多视角应用。
  - 💬 项目文档详尽、功能聚焦，支持高并发视口和布局自定义，适合需要复杂多视角管理的 UE 项目；但依赖 EnhancedInput 插件，可能增加配置步骤。
  🔗 [Fab Marketplace listing](https://www.fab.com/listings/6bc8b467-2ef5-4848-8c26-170893b0998c?tab=%3Ar1e%3A)

- [Houdini Engine for Unreal](https://github.com/sideeffects/HoudiniEngineForUnreal)  Houdini Engine plugin that brings Houdini's procedural workflow into Unreal Engine via Digital Assets.
  - 💬 SideFX官方维护的核心UE插件，将Houdini强大的程序化工作流无缝集成到UE中，是影视特效和程序化内容生成领域的关键工具链。
  🔗 [Website](https://www.sidefx.com/docs/unreal/) · [Side FX's support](https://www.sidefx.com/bugs/submit/) · [Assets documentation.](https://www.sidefx.com/docs/unreal/_assets.html)

- [UnicodeBrowser](https://github.com/ntystudio/UnicodeBrowser)  Unreal Engine Editor Plugin for viewing all supported Unicode Characters.
  - 💬 这是一个针对 Unreal Engine 的 Unicode 字符浏览器插件，功能齐全，解决了编辑器中 Unicode 字符显示异常的痛点，但插件仍处于初期阶段，用户体验有待改进。
  🔗 [UnicodeBlockRange.inl](https://github.com/EpicGames/UnrealEngine/blob/585df42eb3a391efd295abd231333df20cddbcf3/Engine/Source/Runtime/SlateCore/Public/Fonts/UnicodeBlockRange.inl) · [u_charname](https://github.com/unicode-org/icu/blob/f8aa68b0c1c9584633e7a61157185f1a2c275f58/icu4c/source/common/unames.cpp#L1450) · [see this example](https://www.compart.com/en/unicode/search?q=cross#characters)

- [ConfigurableMetasoundMixer](https://github.com/Amir-BK/ConfigurableMetasoundMixer)  A MetaSound mixer with configurable inputs for Unreal Engine 5.6.
  ![ConfigurableMetasoundMixer screenshot](https://github.com/user-attachments/assets/89148099-c0df-4161-8b1d-83e32add8e00)
  - 这是一个基于Unreal Engine 5.6新特性的可配置MetaSound混音器插件。它允许用户指定输入数量，利用可配置节点功能，增强音频工作流程。
  - 💬 该项目展示了UE5.6新功能的实用应用，适用于需要灵活音频混合的开发者。代码结构清晰，但作为新项目，社区影响力有限。

- [World Aware Object](https://github.com/aMustachedPotato/WorldAwareObject)  A UE plugin that adds world context to UObjects for gameplay functionality.
  - World Aware Object 是一个 UE 插件，它为 UObjects 实现了 GetWorld() 功能，使得 SpawnActor、GetGameMode 等节点可以在 UObjects 中使用。支持蓝图和 C++，适用于添加游戏逻辑代码而无需创建完整的 Actor。
  - 💬 该项目实用地解决了 UObjects 缺乏世界上下文的限制，适合需要简化游戏对象逻辑的场景。但作为小型项目，用户基数较小，功能可能较基础。
  🔗 [discord](https://discord.gg/bDfZd2Chg5)

- [Cesium for Unreal](https://github.com/CesiumGS/cesium-unreal)  Cesium for Unreal brings the 3D geospatial ecosystem to Unreal Engine.
  ![Cesium for Unreal screenshot](https://raw.githubusercontent.com/CesiumGS/cesium-unreal/main/Content/Cesium-for-Unreal-Logo-WhiteBGH.jpg)
  ![Cesium for Unreal screenshot](https://prismic-io.s3.amazonaws.com/cesium/b1505fbc-5769-4032-9233-364a4f52acf6_unreal-pipeline-ice-blue-background.png)
  - 💬 这是一个成熟的 Unreal Engine 插件，专注于将高精度 3D 地理空间数据（如地形、影像和建筑）流式传输到 Unreal Engine 中，适用于构建全球尺度的可视化应用。
  🔗 [Cesium ion](https://cesium.com/cesium-ion) · [Cesium for Unreal Homepage](https://cesium.com/cesium-for-unreal?utm_source=github&utm_medium=github&utm_campaign=unreal) · [Download Cesium for Unreal from Unreal Engine Marketplace](https://cesium.com/unreal-marketplace?utm_source=cesium-unreal&utm_medium=github&utm_campaign=unreal)

- [Deduplicate-Plugin](https://github.com/SoulofAO/Deduplicate-Plugin)  Plugin for Removing Duplicates in Unreal Engine Project
  - 💬 该项目提供了一个用于Unreal Engine资产去重的插件，支持多种算法（如基于名称、哈希、SSIM等）进行重复对象检测与合并，适用于优化项目存储和资产管理。星星数较少，可能社区使用范围有限，适合有特定需求的开发者。

- [BDC_LevelSelector](https://github.com/BDCPatrick/BDC_LevelSelector)  A free plugin to add a level selector combobox above the Viewport in Unreal Engine.
  ![BDC_LevelSelector screenshot](https://github.com/BDCPatrick/BDC_LevelSelector/blob/main/Resources/Thumb.png?raw=true)
  ![BDC_LevelSelector screenshot](https://github.com/BDCPatrick/BDC_LevelSelector/blob/main/Resources/Level_Selector_Preview.png?raw=true)
  - 一个免费的 Unreal Engine 编辑器插件，可在视口上方添加一个关卡选择器组合框，递归列出内容浏览器中的所有关卡，方便开发者快速切换。
  - 💬 专注于解决编辑器内快速切换关卡的痛点，功能明确且实用，界面预览看起来比较直观。是一个典型的工具型插件，适合需要频繁测试和跳转多个关卡的开发者。
  🔗 [Level Selector Discord](https://discord.gg/sQmBKETDAm)

- [Metasounds Audio Math Utils](https://github.com/Chris-TopherW/MetasoundsAudioMathUtils)  A collection of audio processing utilities for Metasounds.
  ![Metasounds Audio Math Utils screenshot](https://github.com/Chris-TopherW/MetasoundsAudioMathUtils/assets/11866314/3c56d392-a4f5-4246-ab35-d858daf23569)
  - 这是一个为 Unreal Engine 的 Metasounds 音频系统实现的音频处理工具集，包括包装、幂运算、平方根、门控等功能，旨在扩展音频节点的实用性。
  - 💬 项目提供了实用的音频处理节点，扩展了 Metasounds 的功能，但部分算法如 VCF 可能较重，需注意性能。



## Engine
- [CSLocTools](https://github.com/xabk/CSLocTools) A plugin and a set of engine patches for Unreal Engine 5 that help with localization and string table management.
  - 这是一个非常硬核的本地化重构工具，通过修改引擎源码来实现
  - 对项目内资源文件（Asset Files）的补丁：这是它的核心功能。它会自动修改你的蓝图控件（Widgets）等资源文件（.uasset 文件，这是一种二进制格式的文件），将原本硬编码（in-place）在控件里的文本（FText），替换为对字符串表（String Table）的引用。
  - 解决一个“技术债”（technical debt）问题：项目中已经存在大量硬编码在各个UI控件里的文本，现在需要将它们统一迁移到字符串表中进行管理。这个迁移过程，它通过 Python 脚本、生成 CSV 清单、再通过编辑器命令执行的方式来批量自动化处理




- [MooaToon-Engine](https://github.com/Jason-Ma-0012/MooaToon-Engine) 漫画风卡通渲染引擎 
  - 改了引擎管线，需要作为上游合并到UE5源码
  - 官网 https://mooatoon.com/  
  - 实时的环境交互: 灯光, 阴影, 全局光照等, 就像UE原生的材质一样.
动态的角色表现, 出色的可控性, 同时满足影视和游戏的需求.

- [UnrealEngine-Angelscript](https://github.com/Hazelight/UnrealEngine-Angelscript) AngelScript for Unreal Engine  Angelscript Integration for Unreal Engine
  - 官网 https://angelscript.hazelight.se/
  - 天使脚本引擎，伟大无需多言：UnrealEngine-Angelscript is a set of engine modifications and a plugin for UE5 that integrates a full-featured scripting language.
It is actively developed by Hazelight, creators of Split Fiction and It Takes Two, which were shipped with the majority of their gameplay written in angelscript.

- [NvRTX](https://github.com/NvRTX/UnrealEngine) NvRTX is an optimized and feature-rich branch that contains all the latest developments in the world of ray tracing.
  - 官网 https://developer.nvidia.com/game-engines/unreal-engine/rtx-branch
  - 幻引擎的 NVIDIA RTX™ 分支 (NvRTX) 经过优化，并包含光线追踪和神经图形领域的最新进展
 
- [Moon-Engine](https://github.com/TypeDreamMoon/Moon-Engine) Angel Script & Toon Rendering & NvRTX Unreal Engine
  - 合并了三大上游： AngelScript, Toon Rendering, NvRTX
- [UE-Vite Fork](https://github.com/GapingPixel/UnrealEngineVite-PhysX)  Hyper performant UE Fork with Full-Suite 9th Gen Rendering features distinct to Epic's UE5.
  ![UE-Vite Fork screenshot](https://raw.githubusercontent.com/GapingPixel/UnrealEngineVite-PhysX/ueVite26-release/Images/povray_glasses_s.jpg)
  ![UE-Vite Fork screenshot](https://raw.githubusercontent.com/GapingPixel/UnrealEngineVite-PhysX/ueVite26-release/Images/prism_dispersion_s.jpg)
  ![UE-Vite Fork screenshot](https://raw.githubusercontent.com/GapingPixel/UnrealEngineVite-PhysX/ueVite26-release/Images/swimming_pool_s.jpg)
  - 这是一个对 Unreal Engine 的深度定制分支，旨在提供比 Epic 原版 UE5 更高性能的渲染解决方案。它集成了包括 PhysX、DDGI、TressFX 等在内的一系列经过验证的 AAA 技术，以优化针对当代主机硬件（如 RDNA/Ampere 架构）的帧率和画质表现。
  - 💬 项目目标明确，针对 UE5 在主流主机上的性能痛点提出了激进的优化方案，理念有其价值。但作为大型引擎的分支，其长期维护的复杂度和与上游版本的兼容性将是巨大挑战。
  🔗 [Project files](https://drive.google.com/file/d/1Ya7_Q_HaHfLIs_xAUSr85tjbjY9aMsXy/view?usp=sharing) · [Packaged runnable demo](https://drive.google.com/file/d/1DIwPosfmTZU9uPWi-9JVHWx_75pe40Lz/view?usp=sharing) · [Project files](https://drive.google.com/file/d/1JSl4dASv5SEk4jx_TjEKDEJFBuIscBIn/view?usp=sharing)

- [MassSimple](https://github.com/XistGG/MassSimple)  A simple UE5 Mass C++ example project demonstrating entity registry, creation, destruction, and data management.
  - 💬 这是一个结构清晰、专注于教学的 UE5 Mass 框架入门示例，通过简单的 C++ 代码演示了实体注册、生命周期管理和数据读写等核心概念。代码刻意追求简洁易懂，避免了复杂优化，非常适合作为学习 Mass 框架原理的起点，但直接用于生产环境需要自行进行性能优化。
  🔗 [XistGame-Template](https://github.com/XistGG/XistGame-Template) · [UE5 Git Repository Setup](https://github.com/XistGG/UE5-Git-Init)


- [Unreal-NvRTX5.0-PhysX-ViteStudio](https://github.com/GapingPixel/Unreal-NvRTX5.0-PhysX-ViteStudio)Fork of NvRTX-5.0 (DDGI Optimized) With PhysX, Tessellation (WIP) and Clang 13 compliance
  - 该 Engine Fork 的目标是提供性能最高的虚幻引擎 5 迭代。基于UE NvRTX 5.0版本，之所以不用最新的UE（目前是5.7）是因为新版本的UE性能下降了很多，比如与虚幻引擎 5.6 相比，5.0 版本的移动和碰撞计算速度提高了 2.2 至 2.7 倍，
  
## Script
- [UnrealSharp](https://github.com/UnrealSharp/UnrealSharp) UnrealSharp is a plugin to Unreal Engine 5, which enables developers to create games using C# (.NET 9) with Hot Reload
  - 支持热更新和.NET 生态，NativeAOT编译已经在开发中

- [Puerts](https://github.com/Tencent/puerts) PUER(普洱) Typescript. Let's write your game in UE or Unity with TypeScript.
  - 在Unity支持 AOT 编译；在UE5 没看到相关说明，估计只能JIT，若平台不支持JIT会退化到解释执行

- [UnLua](https://github.com/Tencent/UnLua) A feature-rich, easy-learning and highly optimized Lua scripting plugin for UE.




- [UnrealSpecifiers](https://github.com/fjz13/UnrealSpecifiers)  Detailed explanation of over 100 UE5 specifiers and 300+ meta tags.
  - 这是一个针对 Unreal Engine 5 标识符和元数据的全面参考文档，系统性地整理和解释了上百个核心标识符及超过300个meta标签的用法。项目包含详细的说明文档、配套的示例工程（C++与蓝图），以及相关的演讲资料，旨在弥补官方文档在解释深度上的不足。
  - 💬 项目聚焦于UE开发中频繁使用但官方文档解释不足的‘标识符’和‘meta’，内容组织清晰，兼具实用性和教学价值，是UE5 C++开发者和进阶用户的重要参考工具。
  🔗 [UE5(标识符, meta=(详解, 史上最全)) | 大钊 Epic Games 虚幻社区经理](https://www.bilibili.com/video/BV1152LYrECW/) · [UE5标识符详解 | 史上最全](https://zhuanlan.zhihu.com/p/717920216)



## Python
- [PythonSamples](https://github.com/ue4plugins/PythonSamples)  contains some python samples to script the editor in Unreal Engine.
  - ![alt text](/libraries/images/00_image-5.webp)

- [UnrealEditorPythonScripts](https://github.com/mamoniem/UnrealEditorPythonScripts) Some of my personal scripts i made to use for my own projects
  - ![alt text](/libraries/images/00_image-6.webp)






## Projects

- [AstralShipwright](https://github.com/strangergwenn/AstralShipwright) ASTRAL SHIPWRIGHT / Full game sources for Astral Shipwright, a space sim made with Unreal Engine 5
  ![alt text](/libraries/images/00_image-62.webp)


- [HeliumRain](https://github.com/strangergwenn/HeliumRain) HELIUM RAIN / Full sources for Helium Rain, a realistic space opera using Unreal Engine 4
  ![alt text](/libraries/images/00_image-61.webp)

- [UE5RuntimeToolsFrameworkDemo](https://github.com/gradientspace/UE5RuntimeToolsFrameworkDemo) Sample project/code that uses the UE5 InteractiveToolsFramework to provide a small modeling app at Runtime

- [StateTreeTest](https://github.com/haktan313/StateTreeTest) Advanced AI system using Unreal's State Tree. The enemy can cast magic, switch between passive and aggressive states, and search for health potions with EQS when low on health. Includes 3 different State Tree, several custom tasks, utility selectors, and some logics adapted from my HAIPro plugin, which will support State Tree integration in future.
  ![alt text](/libraries/images/00_image-59.webp)

- [FlowField-RVO2](https://github.com/fukeryester/FlowField-RVO2) A FlowField+RVO2 source code finished with Cursor.
 

- [MaxQ](https://github.com/Gamergenic1/MaxQ) 演示了如果使用NASA的航天规划和分析的行业标准航天工具集（如何引入第三方C语言库）。 spaceflight Toolkit for Unreal Engine 5 
  - https://www.fab.com/listings/8b599b16-39bf-41bd-9ea5-3d1f70d45d06
  ![alt text](/libraries/images/00_image-45.webp)

- [KittensMaze](https://github.com/ukustra/KittensMaze) 一个GAS项目。 A source code of "Kittens' Maze", a free to play game developed in Unreal Engine 4

- [OnAllFronts-Public](https://github.com/HaywireInteractive/OnAllFronts-Public) Mass Entity (ECS) framework Demo 
  - 可以作为City Sample 项目的插件使用
  - https://github.com/Leroy231/ProjectMStarter 主项目
  - ![alt text](/libraries/images/00_image-46.webp)

- [ParagonUIPrototyping](https://github.com/roman-dzieciol/ParagonUIPrototyping) 8年前的UE4项目，可用于学习UI构建。 Paragon UI Prototyping using UE4.11 UMG
  - ![alt text](/libraries/images/00_image-47.webp)

- [ActionRPG_UE53](https://github.com/vahabahmadvand/ActionRPG_UE53) 官方GAS项目升级虚幻5的版本。Action RPG sample project upgraded to the latest Unreal Engine 5.5
  - https://github.com/mirchd/ActionRPG 相似的项目
  - ![alt text](/libraries/images/00_image-48.webp)

- [PixelSpiritDeck](https://github.com/patriciogonzalezvivo/PixelSpiritDeck) 大量Shader基础图形用例学习。 Each Pixel Spirit card presents a visual element together with the GLSL shader code that generates it. Ultimately, these elements can be reused and combined to compose an infinite visual language. This deck is a tool for learning, a library, and an oracle.
  - ![alt text](/libraries/images/00_image-49.webp)

- [MeshCuttingGunSample](https://github.com/HoussineMehnik/MeshCuttingGunSample) 演示物理抓取，和对模型的切割还原。Mesh-Cutting/Restoring mechanics
  - 作者还有更多的开源项目：https://unrealengineresources.com/samples
  - ![alt text](/libraries/images/00_image-50.webp)

- [XFXInfinityBladeEffects](https://github.com/OurGameOrg/XFXInfinityBladeEffects) Epic Games Infinity Blade Effects as a plugin
  - https://www.unrealengine.com/en-US/blog/free-infinity-blade-collection-marketplace-release
  - ![alt text](/libraries/images/00_image-53.webp)

- [PCGExperiments](https://github.com/proceduralit/PCGExperiments)  A collection of Unreal Engine experiments exploring Procedural Content Generation techniques using PCG graphs and custom tools.
  ![PCGExperiments screenshot](/libraries/images/PCGExperiments_image-1.png)
  ![PCGExperiments screenshot](/libraries/images/PCGExperiments_image-2.png)
  ![PCGExperiments screenshot](/libraries/images/PCGExperiments_image-3.png)
  ![PCGExperiments screenshot](/libraries/images/PCGExperiments_image-4.jpg)
  - 这是一个 Unreal Engine 实验集合，专注于使用 PCG 图和自定义工具探索程序化内容生成技术，包括 GPU 纹理采样、书籍生成和曼陀罗图案等应用。
  - 💬 项目展示了 PCG 在 UE 中的多种实用场景，如 GPU 优化和程序化生成，适合学习 PCG 功能，但作为实验集合，代码结构可能不够系统化。

- [PCG DemoRoom](https://github.com/kisspread/DemoRoom)  Unreal Engine 5 PCG DemoRoom for procedural room generation.
  ![PCG DemoRoom screenshot](https://raw.githubusercontent.com/kisspread/DemoRoom/master/Image/img.webp)
  ![PCG DemoRoom screenshot](https://raw.githubusercontent.com/kisspread/DemoRoom/master/Image/1.webp)
  ![PCG DemoRoom screenshot](https://raw.githubusercontent.com/kisspread/DemoRoom/master/Image/2.webp)
  - 这是一个基于 Unreal Engine 5 的 PCG 演示项目，旨在探索使用程序化内容生成技术来精细控制房间生成。项目对比了传统蓝图方法，评估了 PCG 的开发效率和调试优势。
  - 💬 项目展示了 PCG 在精细控制方面的实验性应用，对学习程序化生成有参考价值，但可能需要一定的 UE 和 PCG 基础。

- [Unify](https://github.com/imnazake/Unify)  Demo project demonstrating integration of plugins with Unreal Engine.
  - 这个演示项目展示了如何将我的插件与 Unreal Engine 集成，包括游戏玩法能力系统（Gameplay Ability System）和通用 UI（Common UI）等功能，为开发者提供了一个坚实的基础。
  - 💬 这是一个示例项目，展示了 UE 中 GAS 和 Common UI 的集成，适合作为学习模板，但缺乏独特功能。
  🔗 [here](https://imnazake.github.io/imnazake/docs/unify/features)

- [RogueMassExample](https://github.com/suitsy/RogueMassExample)  A compact UE5.6 sample demonstrating data-oriented simulation with MASS framework.
  ![RogueMassExample screenshot](https://i9.ytimg.com/vi_webp/eJR82WyIl_U/maxresdefault.webp?v=68bf8389&sqp=CIyf1cgG&rs=AOn4CLCanCP1YJQHEIWRxkUPKFsHXsoYJg)
  ![RogueMassExample screenshot](https://i9.ytimg.com/vi_webp/CnftkJcLYxs/sddefault.webp?v=6912e51a&sqp=CLih1cgG&rs=AOn4CLCtKiVaoLANcmj1qNMHPDqm67SNeg)
  - 💬 这是一个针对 Unreal Engine 5.6 MASS 框架的学习示例，结构清晰，适合初学者理解数据导向编程。但作为示例项目，代码可能不够完整，不适合直接用于生产。
  🔗 [![Understand MASS with Unreal Engine](https://i9.ytimg.com/vi_webp/eJR82WyIl_U/maxresdefault.webp?v=68bf8389&sqp=CIyf1cgG&rs=AOn4CLCanCP1YJQHEIWRxkUPKFsHXsoYJg) · [![Understand MASS with Unreal Engine](https://i9.ytimg.com/vi_webp/CnftkJcLYxs/sddefault.webp?v=6912e51a&sqp=CLih1cgG&rs=AOn4CLCtKiVaoLANcmj1qNMHPDqm67SNeg)

- [MetaSounds Synth Repo](https://github.com/msp/MetaSoundsSynthRepo)  A repository for collecting MetaSound synth engines and presets for use in games and interactive experiences.
  - 这是 Unreal Engine 5 MetaSound 合成器的主仓库，用于收集合成引擎和预设，适用于游戏和交互体验项目。它包含了一个功能完整的多音色合成器实现，支持与 UMG 集成进行用户界面控制。
  - 💬 该项目提供了 UE5 MetaSounds 的实用参考实现，亮点在于多音色合成和 UMG 集成，适合音频设计师快速原型设计，但 Haskell 语言标签可能与主要 Blueprint/资产结构不符。
  🔗 [AudioKit Synth One](https://audiokitpro.com/synth/) · ["Unreal Engine MetaSounds"](https://dev.epicgames.com/community/learning/tutorials/Kw7l/unreal-engine-metasounds) · [code samples](https://github.com/msp/6070-intro-to-metasounds?tab=readme-ov-file)



## Other
- [msdfgen](https://github.com/Chlumsky/msdfgen) Multi-channel signed distance field generator
  - 多通道 signed distance field 生成器



- [UnrealVerse](https://github.com/VerseMetaVerse/UnrealVerse) Information and links about Epic's Unreal Engine including Verse programming language for UEFN, Unreal, Fortnite and the Metaverse along with UE5 and the UE6 convergence

- [flecs](https://github.com/SanderMertens/flecs) A fast entity component system (ECS) for C & C++
  - Flecs 是一个快速轻量级的实体组件系统，可让您使用数百万个实体构建游戏和模拟。
  - ![alt text](https://github.com/SanderMertens/flecs/raw/master/docs/img/explorer.webp)
  - ![alt text](/libraries/images/00_image-69.webp)
  - 提供用于分析 ECS 性能的统计插件，以及用于监视和控制您的应用程序的基于 Web 的 UI
  - 使用 emscripten 无需修改即可在浏览器中运行

- [UE_Modding](https://github.com/Dmgvol/UE_Modding) A collection of UE4 (and 5) Modding Guides.
The perfect place for anyone new, to learn UE modding and start creating mods today.
  - 虚幻引擎第三方魔改模组开发指南

- [cheat-engine](https://github.com/cheat-engine/cheat-engine) Cheat Engine is a development environment focused on modding games and applications for personal use.
  ![alt text](/libraries/images/00_image-57.webp)

- [lua-bytecode-parser-ce](https://github.com/std-microblock/lua-bytecode-parser-ce) A versatile Lua 5.3 bytecode parser that supports both standard Lua bytecode and Cheat Engine modified format.

- [lazygit](https://github.com/jesseduffield/lazygit) simple terminal UI for git commands


- [avbd-demo2d](https://github.com/savant117/avbd-demo2d) Augmented Vertex Block Descent (AVBD) reference implementation
  <video src="https://graphics.cs.utah.edu/research/projects/avbd/teaser.mp4" controls autoplay loop> 
    Your browser does not support the video tag.
  </video>



- [audivis-relay](https://github.com/std-microblock/audivis-relay) Audivis Relay 是一款轻量级的麦克风串流软件，能够将物理麦克风的音频实时传输到虚拟麦克风设备，适用于远程会议、直播、语音聊天等场景。
  ![alt text](/libraries/images/00_image-52.webp)

- [Mesh2Motion](https://github.com/scottpetrovic/mesh2motion-app) Import a 3D Model and automatically assign and export animations with Mesh2Motion. This is kind of similar to a web application like Mixamo, but I would like it to be more flexible so it can support other model and skeleton types. Hopefully the open source nature means it can be expanded on and evolve more than than the closed tools have.

- [Noclip.website](https://github.com/magcius/noclip.website) A digital museum of video game levels
  - https://noclip.website/
  - [load level](https://noclip.website/#mkwii/castle_course;ShareData=AFkg2UaBz~8hs}oUG8C!VdHbcQRDYPUiNfVTdmxYV+xla9Xs0J85XnoUnEj3WP)
  - ![alt text](/libraries/images/00_image-51.webp)


- [awesome-unreal](https://github.com/insthync/awesome-unreal) Some Unreal Engine  Tools

- [highway](https://github.com/google/highway) Performance-portable, length-agnostic SIMD with runtime dispatch

- [autogen](https://github.com/microsoft/autogen) AutoGen is a framework for creating multi-agent AI applications that can act autonomously or work alongside humans.

- [dify](https://github.com/langgenius/dify) Dify is an open-source LLM app development platform. Its intuitive interface combines agentic AI workflow, RAG pipeline, agent capabilities, model management, observability features and more, letting you quickly go from prototype to production.

- [airi](https://github.com/moeru-ai/airi) 💖🧸 Self hosted, you owned Grok Companion, a container of souls of waifu, cyber livings to bring them into our worlds, wishing to achieve Neuro-sama's altitude. Capable of realtime voice chat, Minecraft, Factorio playing. Web / macOS / Windows supported.
  ![alt text](/libraries/images/00_image-54.webp)








 
