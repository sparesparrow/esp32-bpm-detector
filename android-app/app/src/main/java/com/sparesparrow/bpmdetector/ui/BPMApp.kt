package com.sparesparrow.bpmdetector.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.sparesparrow.bpmdetector.ui.screens.BPMDisplayScreen
import com.sparesparrow.bpmdetector.ui.screens.SettingsScreen
import com.sparesparrow.bpmdetector.viewmodels.BPMViewModel

/**
 * Main app composable with navigation
 */
@Composable
fun BPMApp(viewModel: BPMViewModel) {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            BPMBottomNavigation(navController = navController)
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.BPMDisplay.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.BPMDisplay.route) {
                BPMDisplayScreen(viewModel = viewModel)
            }
            composable(Screen.Settings.route) {
                SettingsScreen(viewModel = viewModel)
            }
        }
    }
}

/**
 * Bottom navigation bar
 */
@Composable
fun BPMBottomNavigation(navController: NavHostController) {
    val items = listOf(
        Screen.BPMDisplay,
        Screen.Settings
    )

    NavigationBar {
        val navBackStackEntry by navController.currentBackStackEntryAsState()
        val currentRoute = navBackStackEntry?.destination?.route

        items.forEach { screen ->
            NavigationBarItem(
                icon = { Icon(screen.icon, contentDescription = screen.title) },
                label = { Text(screen.title) },
                selected = currentRoute == screen.route,
                onClick = {
                    navController.navigate(screen.route) {
                        // Pop up to the start destination of the graph to
                        // avoid building up a large stack of destinations
                        // on the back stack as users select items
                        navController.graph.startDestinationRoute?.let { route ->
                            popUpTo(route) {
                                saveState = true
                            }
                        }
                        // Avoid multiple copies of the same destination when
                        // reselecting the same item
                        launchSingleTop = true
                        // Restore state when reselecting a previously selected item
                        restoreState = true
                    }
                }
            )
        }
    }
}

