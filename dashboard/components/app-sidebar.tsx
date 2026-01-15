"use client"

import { Home, MessageCircle, Settings } from "lucide-react"
import { usePathname } from "next/navigation"
import { useMemo } from "react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Link } from "@/i18n/navigation"
import { useExtracted } from "next-intl"

export function AppSidebar() {
  const t = useExtracted()
  const pathname = usePathname()

  const items = [
    {
      title: t("Home"),
      url: "/",
      icon: Home,
    },
    {
      title: t("Chats"),
      url: "/chats",
      icon: MessageCircle,
    },
    {
      title: t("Settings"),
      url: "/settings",
      icon: Settings,
    },
  ]

  const isActive = useMemo(
    () => (url: string) => {
      if (url === "/") {
        return pathname === "/" || !!/^\/[a-z]{2}$/.test(pathname)
      }
      return pathname.includes(url)
    },
    [pathname],
  )

  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Application</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map(item => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    isActive={isActive(item.url)}
                    render={props => <Link href={item.url} {...props} />}
                  >
                    <item.icon />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
